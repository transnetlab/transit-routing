"""
Builds the Time expanded Graph.
"""
import sys
from time import time

from tqdm import tqdm

from miscellaneous_func import *


def initialize() -> tuple:
    """
    Takes the required inputs for building Time expanded graph

    Returns:
        breaker (str): string
        GENERATE_LOGFILE (int): 1 to redirect and save a log file. Else 0
        start_time: timestamp object

    Examples:
        >>> breaker, start_time, GENERATE_LOGFILE = initialize()

    """
    breaker = "________________________________________________________________"
    print(breaker)
    print("Building Time expanded graph. Enter following parameters.\n")
    import psutil
    print(f'RAM {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB (% used:{psutil.virtual_memory()[2]})')
    GENERATE_LOGFILE = int(input(f"Press 1 to redirect output to a log file in logs folder. Else press 0. Example: 0\n: "))
    if not os.path.exists(f'./logs/.'):
        os.makedirs(f'./logs/.')
    if not os.path.exists(f'./Data/time_expanded/{NETWORK_NAME}'):
        os.makedirs(f'./Data/time_expanded/{NETWORK_NAME}')

    start_time = time()

    return breaker, start_time, GENERATE_LOGFILE


def add_edges_for_trips(stop_times_file, nodes_dict: dict) -> list:
    """
    Adds edges corresponding to trips

    Args:
        stop_times_file (pandas.dataframe): dataframe with stoptimes details.
        nodes_dict (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Returns:
        trip_edges (list): list of tuples of format: [(from node id, to node id, weight)]

    Examples:
        >>> trip_edges = add_edges_for_trips(stop_times_file, nodes_dict)
    """
    print("adding edges corresponding to trips...")
    t1 = time()
    trip_edges = []
    trip_groups = stop_times_file.groupby("trip_id")
    for tid, trip in tqdm(trip_groups):
        trip.sort_values(by='stop_sequence', inplace=True)
        for x in range(len(trip) - 1):
            row1, row2 = trip.iloc[x], trip.iloc[x + 1]
            trip_edges.append(
                (nodes_dict[(row1.stop_id, row1.arrival_time)], nodes_dict[(row2.stop_id, row2.arrival_time)],
                 int((row2.arrival_time - row1.arrival_time).total_seconds())))
    print(f"Time required to add trip edges: {round((time() - t1) / 60, 2)} minutes")
    print(breaker)
    return trip_edges


def add_edges_for_footpaths(stop_times_file, nodes_dict: dict, transfers_file) -> list:
    """
    Adds edges corresponding to footpaths

    Args:
        stop_times_file (pandas.dataframe): dataframe with stoptimes details.
        transfers_file (pandas.dataframe): dataframe with transfers (footpath) details.
        nodes_dict (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Returns:
        foot_connection (list): list of tuples of format: [(from node id, to node id, weight)]

    Examples:
        >>> foot_connections = add_edges_for_footpaths(stop_times_file, nodes_dict, transfers_file)

    """
    print("adding edges corresponding to footpaths...")
    t2 = time()
    foot_connections = []
    temp = list(transfers_file.from_stop_id)
    temp.extend(transfers_file.to_stop_id)
    temp = stop_times_file[stop_times_file.stop_id.isin(set(temp))]
    t = temp[['stop_id', 'arrival_time']].groupby("stop_id")
    for _, trans in tqdm(transfers_file.iterrows()):
        from_nodes = list(t.get_group(trans.from_stop_id).itertuples(index=False, name=None))
        to_nodes = list(t.get_group(trans.to_stop_id).itertuples(index=False, name=None))
        foot_connections.extend(
            [(nodes_dict[s], nodes_dict[d], (d[1] - s[1]).total_seconds()) for s in from_nodes for d in to_nodes if
             (d[1] - s[1]).total_seconds() >= trans.min_transfer_time])
    print(f"Time required to add footpath edges: {round((time() - t2) / 60, 2)} minutes")
    print(breaker)
    return foot_connections


def add_transfer_edges(stop_times_file, nodes_dict: dict) -> list:
    """
    Adds transfer edges between nodes

    Args:
        stop_times_file (pandas.dataframe): dataframe with stoptimes details.
        nodes_dict (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Returns:
        transfer_edges (list): list of tuples of format: [(from node id, to node id, weight)]

    Examples:
        >>> transfer_edges = add_transfer_edges(stop_times_file, nodes_dict)

    """
    print("Adding waiting edges...")
    t3 = time()
    transfer_edges = []
    t = stop_times_file[['stop_id', 'arrival_time']].groupby("stop_id")
    for _, stop_Det in tqdm(t):
        transfer_edge = list(stop_Det.sort_values('arrival_time').itertuples(index=False, name=None))
        for pointer in range(len(stop_Det) - 1):
            transfer_edges.append(
                (nodes_dict[transfer_edge[pointer]], nodes_dict[transfer_edge[pointer + 1]],
                 int((transfer_edge[pointer + 1][1] - transfer_edge[pointer][1]).total_seconds())))
    print(f"Time required to add transfer edges: {round((time() - t3) / 60, 2)} minutes")
    print(breaker)
    return transfer_edges


def combine_edges(trip_edges: list, foot_connections: list, transfer_edges: list) -> list:
    """
    Combines all 3 types of edges into a single list (trip, footpath, and transfer)

    Args:
        trip_edges (list) : list of tuples of format: [(from node id, to node id, weight)]
        foot_connections (list) : list of tuples of format: [(from node id, to node id, weight)]
        transfer_edges (list): list of tuples of format: [(from node id, to node id, weight)]

    Returns:
        edges (list): list of tuples of format: [(from node id, to node id, weight)]

    Examples:
        >>> edge_list = combine_edges(trip_edges, foot_connections, transfer_edges)

    """
    print("Combining all edges...")
    t4 = time()
    edges = []
    edges.extend(trip_edges)
    del (trip_edges)
    edges.extend(foot_connections)
    del (foot_connections)
    edges.extend(transfer_edges)
    del (transfer_edges)
    print(f"Time required to combine transfer edges: {round((time() - t4) / 60, 2)} minutes")
    print(breaker)
    return edges


def dump_edges_dict(edges: list, NETWORK_NAME: str) -> None:
    """
    Saves the edges list as a pickle file

    Args:
        edges (list): list of tuples of format: [(from node id, to node id, weight)]
        NETWORK_NAME (str): name of the network

    Returns:
        None

    Examples:
        >>> dump_edges_dict(edges, 'anaheim')

    """
    print("Saving edges file")
    with open(f"./Data/time_expanded/{NETWORK_NAME}/TE_{NETWORK_NAME[2:]}_edges.pkl", "wb") as file:
        pickle.dump(edges, file)
    return None


def dump_graph_dict(edges: list, NETWORK_NAME: str, nodes_dict: dict) -> None:
    """
    Builds and saves a networkx multigraph object.

    Args:
        edges: list of edges. Format: [(from stop, to stop, weight)]
        NETWORK_NAME (str): name of the network
        nodes_dict (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Returns:
        None

    Examples:
        >>> dump_graph_dict(edges, 'anaheim', nodes_dict)
    """
    print("Building and saving graph object")
    G = nx.MultiDiGraph()
    G.add_weighted_edges_from(edges)
    del (edges)
    del (nodes_dict)
    with open(f"./Data/time_expanded/{NETWORK_NAME}/graph_{NETWORK_NAME}", 'wb') as file:
        pickle.dump(G, file)
    print(f"TE graph for {NETWORK_NAME}: \n Nodes {G.number_of_nodes()} \n Edges {G.number_of_edges()}")
    print(breaker)
    return None


def main() -> None:
    """
    Main function

    Returns:
        None

    Examples:
        >>> main()

    """
    temp = stop_times_file[['stop_id', 'arrival_time']].drop_duplicates().reset_index(drop=True)
    nodes_dict = {stop_stamp: idx for idx, stop_stamp in enumerate(list(zip(temp['stop_id'], temp['arrival_time'])), 1)}

    trip_edges = add_edges_for_trips(stop_times_file, nodes_dict)

    foot_connections = add_edges_for_footpaths(stop_times_file, nodes_dict, transfers_file)

    transfer_edges = add_transfer_edges(stop_times_file, nodes_dict)

    edges = combine_edges(trip_edges, foot_connections, transfer_edges)

    dump_edges_dict(edges, NETWORK_NAME)

    dump_graph_dict(edges, NETWORK_NAME, nodes_dict)

    end = (time() - start_time) / 60
    print(f"Total Time: {round(end, 2)} minutes")
    return None


if __name__ == '__main__':
    with open(f'./parameters_entered.txt', 'rb') as file:
        parameter_files = pickle.load(file)
    BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TRANSFER_PATTERNS_FILES, BUILD_CSA = parameter_files
    # BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES = 1, "anaheim", 1
    BUILD_TE = 1
    if BUILD_TE == 1:
        breaker, start_time, GENERATE_LOGFILE = initialize()
        stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = read_testcase(
            NETWORK_NAME)
        if GENERATE_LOGFILE == 1:
            sys.stdout = open(f'./logs/TE_builder_{NETWORK_NAME}', 'w')
        main()
