"""
Builds the transfer.txt file.
"""
import multiprocessing
import pickle
from multiprocessing import Pool
from time import time
import os, sys

import networkx as nx
import numpy as np
import pandas as pd
from haversine import haversine_vector, Unit
from tqdm import tqdm



def extract_graph(NETWORK_NAME: str, breaker: str) -> tuple:
    """
    Extracts the required OSM.

    Args:
        NETWORK_NAME (str): name of the network
        stops_list (list):

    Returns:
        networkx graph, list of tuple [(stop id, nearest OSM node)]

    Examples:
        >>> G, stops_list = extract_graph("anaheim", breaker)
    """
    try:
        G = pickle.load(open(f"./Data/GTFS/{NETWORK_NAME}/gtfs_o/{NETWORK_NAME}_G.pickle", 'rb'))
        # G = nx.read_gpickle(f"./GTFS/{NETWORK_NAME}/gtfs_o/{NETWORK_NAME}_G.pickle")
        print("Graph imported from disk")
    except (FileNotFoundError, ValueError, AttributeError) as error:
        print(f"Graph import failed {error}. Extracting OSM graph for {NETWORK_NAME}")
        G = ox.graph_from_place(f"{NETWORK_NAME}", network_type='drive')
        # TODO: Change this to bound box + 1 km
        print(f"Number of Edges: {len(G.edges())}")
        print(f"Number of Nodes: {len(G.nodes())}")
        print(f"Saving {NETWORK_NAME}")
        pickle.dump(G, open(f"./Data/GTFS/{NETWORK_NAME}/gtfs_o/{NETWORK_NAME}_G.pickle", 'wb'))
        # nx.write_gpickle(G, f"./GTFS/{NETWORK_NAME}/gtfs_o/{NETWORK_NAME}_G.pickle")
    stops_db = pd.read_csv(f'./Data/GTFS/{NETWORK_NAME}/stops.txt')
    stops_db = stops_db.sort_values(by='stop_id').reset_index(drop=True)
    stops_list = list(stops_db.stop_id)
    try:
        osm_nodes = ox.nearest_nodes(G, stops_db.stop_lon.to_list(), stops_db.stop_lat.to_list())
    except:
        print("Warning: OSMnx.nearest_nodes failed. Switching to Brute force for finding nearest OSM node...")
        print("Fix the above import for faster results")
        node_names, node_coordinates = [], []
        for node in G.nodes(data=True):
            node_coordinates.append((node[1]["y"], node[1]["x"]))
            node_names.append(node[0])
        dist_list = []
        for _, stop in tqdm(stops_db.iterrows()):
            dist_list.append(haversine_vector(node_coordinates, len(node_coordinates) * [(stop.stop_lat, stop.stop_lon)], unit=Unit.METERS))
        osm_nodes = [node_names[np.argmin(item)] for item in dist_list]
        print(f"Unique STOPS: {len(stops_db)}")
        print(f"Unique OSM nodes identified: {len(set(osm_nodes))}")
    stops_list = list(zip(stops_list, osm_nodes))
    print(breaker)
    return G, stops_list


def find_transfer_len(source_info: tuple) -> list:
    """
    Runs shortest path algorithm from source stop with cutoff limit of WALKING_LIMIT * 2

    Args:
        source_info (tuple): Format (stop id, nearest OSM node)

    Returns:
        temp_list (list): list of format: [(bus stop id, osm node id, distance between the two nodes)]

    Examples:
        >>> temp_list = find_transfer_len(source_info)
    """
    # print(source_info[0])
    out = nx.single_source_dijkstra_path_length(G, source_info[1], cutoff=WALKING_LIMIT * 2, weight='length')
    reachable_osmnodes = set(out.keys())
    temp_list = [(source_info[0], stopid, round(out[osm_nodet], 1)) for (stopid, osm_nodet) in stops_list if osm_nodet in reachable_osmnodes]
    return temp_list


def transitive_closure(input_list: tuple) -> list:
    """
    Ensures transitive closure of footpath graph

    Args:
        input_list (tuple): list of format [(network graph object)]

    Returns:
        new_edges (list):

    """
    graph_object, connected_component = input_list
    new_edges = []
    for source in connected_component:
        for desti in connected_component:
            if source != desti and (source, desti) not in G_new.edges():
                new_edges.append((source, desti, nx.dijkstra_path_length(G_new, source, desti, weight="length")))
    return new_edges


def post_process(G_new, NETWORK_NAME: str, ini_len: int) -> None:
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
    footpath = list(G_new.edges(data=True))
    reve_edges = [(x[1], x[0], x[-1]) for x in G_new.edges(data=True)]
    footpath.extend(reve_edges)
    transfer_file = pd.DataFrame(footpath)
    transfer_file[2] = transfer_file[2].apply(lambda x: list(x.values())[0])
    transfer_file.rename(columns={0: "from_stop_id", 1: "to_stop_id", 2: "min_transfer_time"}, inplace=True)
    transfer_file.sort_values(by=['min_transfer_time', 'from_stop_id', 'to_stop_id']).reset_index(drop=True)
    transfer_file.to_csv(f"./DATA/GTFS/{NETWORK_NAME}/transfers.csv", index=False)
    transfer_file.to_csv(f"./DATA/GTFS/{NETWORK_NAME}/transfers.txt", index=False)
    print(f"Before Transitive closure: {ini_len}")
    print(f"After  Transitive closure (final file): {len(transfer_file)}")
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
        USE_PARALlEL (int): 1 for parallel and 0 for serial
        GENERATE_LOGFILE (int): 1 to redirect and save a log file. Else 0

    Warnings:
        Building Transfers file requires OSMnX module.

    Examples:
    >>> breaker, G, stops_list, CORES, WALKING_LIMIT, start_time, USE_PARALlEL, GENERATE_LOGFILE = initialize()


    """
    breaker = "________________________________________________________________"
    print(breaker)
    print("Building transfers file. Enter following parameters.\n")

    WALKING_LIMIT = int(input("Enter maximum allowed walking limit in seconds. Format: YYYYMMDD. Example: 180\n: "))
    USE_PARALlEL = int(
        input("Transfer.txt can be built in parallel. Enter 1 to use multiprocessing in shortest path computation. Else press 0. Example: 0\n: "))
    CORES = 0
    if USE_PARALlEL != 0:
        CORES = int(input(f"Enter number of CORES (>=1). \nAvailable cores (logical and physical):  {multiprocessing.cpu_count()}\n: "))

    print(f'RAM {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB (% used:{psutil.virtual_memory()[2]})')
    start_time = time()
    GENERATE_LOGFILE = int(input(f"Press 1 to redirect output to a log file in logs folder. Else press 0. Example: 0\n: "))
    if not os.path.exists(f'./logs/.'):
        os.makedirs(f'./logs/.')

    G, stops_list = extract_graph(NETWORK_NAME, breaker)
    # stops_db = stops_db.sort_values(by='stop_id').reset_index(drop=True).reset_index().rename(columns={"index": 'new_stop_id'})
    return breaker, G, stops_list, CORES, WALKING_LIMIT, start_time, USE_PARALlEL, GENERATE_LOGFILE


if __name__ == '__main__':
    with open(f'./parameters_entered.txt', 'rb') as file:
        parameter_files = pickle.load(file)
    BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TRANSFER_PATTERNS_FILES, BUILD_CSA = parameter_files
    # BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES = 1, "Atlanta", 1
    if BUILD_TRANSFER == 1:
        # Import at top create Sphinx error
        import osmnx as ox
        import psutil
        ox.settings.use_cache = True
        ox.settings.log_console = False

        breaker, G, stops_list, CORES, WALKING_LIMIT, start_time, USE_PARALlEL, GENERATE_LOGFILE = initialize()
        if GENERATE_LOGFILE == 1:
            sys.stdout = open(f'./logs/Transfer_builder{NETWORK_NAME}', 'w')

        if USE_PARALlEL != 0:
            with Pool(CORES) as pool:
                result = pool.map(find_transfer_len, stops_list)
        else:
            result = [find_transfer_len(source_info) for source_info in tqdm(stops_list)]
        print(breaker)
        stops_db, osm_nodes, G = 0, 0, 0
        result = [item2 for item in result for item2 in item]
        transfer_file = pd.DataFrame(result, columns=['from_stop_id', 'to_stop_id', 'min_transfer_time'])

        # Post-processing section
        transfer_file = transfer_file[transfer_file.from_stop_id != transfer_file.to_stop_id].drop_duplicates(subset=['from_stop_id', 'to_stop_id'])
        transfer_file = transfer_file[(transfer_file.min_transfer_time < WALKING_LIMIT) & (transfer_file.min_transfer_time > 0)].reset_index(drop=True)
        transfer_file.to_csv(f'./DATA/GTFS/{NETWORK_NAME}/gtfs_o/transfers.csv', index=False)
        transfer_file.to_csv(f'./DATA/GTFS/{NETWORK_NAME}/gtfs_o/transfers.txt', index=False)
        ini_len = len(transfer_file)
        G_new = nx.Graph()  # Ensure transitive closure of footpath graph
        edges = list(zip(transfer_file.from_stop_id, transfer_file.to_stop_id, transfer_file.min_transfer_time))
        G_new.add_weighted_edges_from(edges)
        connected_compnent_list = [(G_new, c) for c in nx.connected_components(G_new)]
        print(f"Total connected components identified: {len(connected_compnent_list)}")
        if USE_PARALlEL != 0:
            print("Ensuring Transitive closure in parallel...")
            with Pool(CORES) as pool:
                new_edge_list = pool.map(transitive_closure, connected_compnent_list)
            new_edge_list = [y for x in new_edge_list for y in x]
        else:
            print("Ensuring Transitive closure in serial...")
            new_edge_list = [transitive_closure(input_list) for input_list in tqdm(connected_compnent_list)]
            new_edge_list = [y for x in new_edge_list for y in x]
        G_new.add_weighted_edges_from(new_edge_list)
        post_process(G_new, NETWORK_NAME, ini_len)
        if GENERATE_LOGFILE == 1: sys.stdout.close()
    else:
        try:
            transfer_file = pd.read_csv(f'./Data/GTFS/{NETWORK_NAME}/gtfs_o/transfers.txt')
            transfer_file.to_csv(f'./Data/GTFS/{NETWORK_NAME}/transfers.txt', index=False)
            print("Using  Transfers.txt found in GTFS set. Warning: Ensure that transfers are transitively closed.")
        except FileNotFoundError:
            print("Transfers file missing. Either build the file by setting BUILD_TRANSFER to 1 or place transfers.txt in zip file.")
