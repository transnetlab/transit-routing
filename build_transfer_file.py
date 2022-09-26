"""
Builds the transfer.txt file.
"""
import networkx as nx
import osmnx as ox
import multiprocessing
from multiprocessing import Pool
import pandas as pd
import psutil
from tqdm import tqdm
from time import time
import pickle


def extract_graph(NETWORK_NAME: str, breaker: str) -> tuple:
    """
    Extracts the required OSM.
    Args:
        NETWORK_NAME (str): Network name

    Returns:
        networkx graph, list of tuple [(stop id, nearest OSM node)]
    """
    try:
        G = nx.read_gpickle(f"./GTFS/{NETWORK_NAME}/gtfs_o/{NETWORK_NAME}_G.pickle")
        print("Graph imported from disk")
    except FileNotFoundError:
        print(f"Extracting OSM graph for {NETWORK_NAME}")
        G = ox.graph_from_place(f"{NETWORK_NAME}", network_type='drive')
        print(f"Number of Edges: {len(G.edges())}")
        print(f"Number of Nodes: {len(G.nodes())}")
        print(f"Saving {NETWORK_NAME}")
        nx.write_gpickle(G, f"./GTFS/{NETWORK_NAME}/gtfs_o/{NETWORK_NAME}_G.pickle")
    stops_db = pd.read_csv(f'./GTFS/{NETWORK_NAME}/stops.txt')
    stops_db = stops_db.sort_values(by='stop_id').reset_index(drop=True)
    stops_list = list(stops_db.stop_id)
    osm_nodes = ox.nearest_nodes(G, stops_db.stop_lon.to_list(), stops_db.stop_lat.to_list())
    stops_list = list(zip(stops_list, osm_nodes))
    print(breaker)
    return G, stops_list


def parallel_func(source_info: tuple) -> list:
    """
    Runs shortest path algorithm from source stop with cutoff limit of WALKING_LIMIT * 2
    Args:
        source_info (tuple): Format (stop id, nearest OSM node)

    Returns:
        list of
    """
    # print(source_info[0])
    out = nx.single_source_dijkstra_path_length(G, source_info[1], cutoff=WALKING_LIMIT * 2, weight='length')
    reachable_osmnodes = set(out.keys())
    temp_list = [(source_info[0], stopid, round(out[osm_nodet], 1)) for (stopid, osm_nodet) in stops_list if osm_nodet in reachable_osmnodes]
    return temp_list


def post_process(transfer_file, WALKING_LIMIT: int, NETWORK_NAME: str) -> None:
    """
    Post process the transfer file. Following functionality are included:
        1. Checks if the transfers graph is transitively closed.
    Args:
        transfer_file: GTFS transfers.txt file
        WALKING_LIMIT (int): Maximum walking limit
        NETWORK_NAME (str): Network name

    Returns:
        None
    """
    transfer_file.to_csv(f'./GTFS/{NETWORK_NAME}/gtfs_o/transfers.csv', index=False)
    transfer_file.to_csv(f'./GTFS/{NETWORK_NAME}/gtfs_o/transfers.txt', index=False)

    print("Post processing transfers file")
    transfer_file = transfer_file[transfer_file.from_stop_id != transfer_file.to_stop_id].drop_duplicates(subset=['from_stop_id', 'to_stop_id'])
    transfer_file = transfer_file[(transfer_file.min_transfer_time < WALKING_LIMIT) & (transfer_file.min_transfer_time > 0)].reset_index(drop=True)

    G = nx.Graph()  # Ensure transitive closure of footpath graph
    edges = list(zip(transfer_file.from_stop_id, transfer_file.to_stop_id, transfer_file.min_transfer_time))
    G.add_weighted_edges_from(edges)
    connected = [c for c in nx.connected_components(G)]
    for tree in tqdm(connected):
        for source in tree:
            for desti in tree:
                if source != desti and (source, desti) not in G.edges():
                    G.add_edge(source, desti, weight=nx.dijkstra_path_length(G, source, desti))
    footpath = list(G.edges(data=True))
    reve_edges = [(x[1], x[0], x[-1]) for x in G.edges(data=True)]
    footpath.extend(reve_edges)
    transfer_file = pd.DataFrame(footpath)
    transfer_file[2] = transfer_file[2].apply(lambda x: list(x.values())[0])
    transfer_file.rename(columns={0: "from_stop_id", 1: "to_stop_id", 2: "min_transfer_time"}, inplace=True)
    transfer_file.sort_values(by=['min_transfer_time', 'from_stop_id', 'to_stop_id']).reset_index(drop=True)
    transfer_file.to_csv(f"./GTFS/{NETWORK_NAME}/transfers.csv", index=False)
    transfer_file.to_csv(f"./GTFS/{NETWORK_NAME}/transfers.txt", index=False)
    print(f"Total transfers: {len(transfer_file)}")
    print(f"Longest transfer: {transfer_file.iloc[-1].min_transfer_time} seconds")
    print(f"Time required: {round((time() - start_time) / 60, 1)} minutes")
    print(breaker)
    return None


def initialize() -> tuple:
    """
    Initialize variables for building transfers file.

    Returns:
        breaker (str): print line breaker
        G: Network graph of NETWORK NAME
        stops_list (list):
        CORES (int): Number of codes to be used
        WALKING_LIMIT (int): Maximum allowed walking time
        start_time: timestamp object
    """
    breaker = "________________________________________________________________"
    print(breaker)
    print("Building transfers file. Enter following parameters.\n")
    WALKING_LIMIT = int(input("Enter maximum allowed walking limit in seconds. Format: YYYYMMDD. Example: 180\n: "))
    CORES = int(input(
        f"Transfer.txt can be build in parallel. Enter number of CORES (1 for serial). \nAvailable cores (logical and physical):  {multiprocessing.cpu_count()}\n: "))

    ox.config(use_cache=True, log_console=False)
    print(f'RAM {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB (% used:{psutil.virtual_memory()[2]})')
    start_time = time()

    G, stops_list = extract_graph(NETWORK_NAME, breaker)
    # stops_db = stops_db.sort_values(by='stop_id').reset_index(drop=True).reset_index().rename(columns={"index": 'new_stop_id'})
    # stops_list = stops_list[:10]
    print(f"Running shortest path on {CORES} CORES")
    return breaker, G, stops_list, CORES, WALKING_LIMIT, start_time


if __name__ == '__main__':
    with open(f'parameters_entered.txt', 'rb') as file:
        parameter_files = pickle.load(file)
    BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES = parameter_files
    if BUILD_TRANSFER == 1:
        breaker, G, stops_list, CORES, WALKING_LIMIT, start_time = initialize()
        with Pool(CORES) as pool:
            result = pool.map(parallel_func, stops_list)
        print(breaker)
        stops_db, osm_nodes, G = 0, 0, 0
        result = [item2 for item in result for item2 in item]
        transfer_file = pd.DataFrame(result, columns=['from_stop_id', 'to_stop_id', 'min_transfer_time'])
        post_process(transfer_file, WALKING_LIMIT, NETWORK_NAME)
    else:
        try:
            transfer_file = pd.read_csv(f'./GTFS/{NETWORK_NAME}/gtfs_o/transfers.txt')
        except FileNotFoundError:
            print("Transfers file missing. Either build the file by setting BUILD_TRANSFER to 1 or place transfers.txt in zip file.")
