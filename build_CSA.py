"""
Builds structures related to transfer patterns
"""
import multiprocessing
from multiprocessing import Pool
from time import time

from tqdm import tqdm

from miscellaneous_func import *


def initialize() -> tuple:
    """
    Initialize variables for building transfers file.

    Returns:
        breaker (str): print line breaker
        start_time: timestamp object
        USE_PARALlEL (int): 1 for parallel and 0 for serial
        CORES (int): Number of codes to be used
        start_time = time()

    """
    breaker = "________________________________________________________________"
    print(breaker)
    USE_PARALlEL = int(
        input("CSA can be built in parallel. Enter 1 to use multiprocessing in shortest path computation. Else press 0. Example: 0\n: "))
    CORES = 0
    if USE_PARALlEL != 0:
        CORES = int(input(f"Enter number of CORES (>=1). \nAvailable cores (logical and physical):  {multiprocessing.cpu_count()}\n: "))
    start_time = time()

    return breaker, USE_PARALlEL, CORES, start_time


def extract_connections(route_trips: tuple) -> list:
    """
    For a given route id, extract all connections form its trips.

    Args:
        route_trips (tuple):  Format: route id, list of trips.

    Returns:
        route_connections (list): list of tuples. format: [(from stop, to stop, from time, to time, trip id)].

    """
    route, trip_list = route_trips
    route_connections = []
    for tid, trip in enumerate(trip_list):
        connections = list(zip(trip[:-1], trip[1:]))
        route_connections.extend(
            [(from_stop, to_stop, from_time, to_time, f'{route}_{tid}') for ((from_stop, from_time), (to_stop, to_time)) in connections])
    return route_connections


def process_csa_array(connections_list) -> list:
    """
    Processing function for CSA build. Currently supported functionality are:
    1. Filter connections with from stop == to stop and departure time == arrival time
    2. Sort the connection array
    #TODO: Better sort function

    Args:
        connections_list (list): list of tuples. format: [(from stop, to stop, from time, to time, trip id)].

    Returns:
        connections_list (list): list of tuples. format: [(from stop, to stop, from time, to time, trip id)].

    """
    print("Applying sanity checks...")
    print(" A. Build dataframe...")
    ini_len = len(connections_list)
    connections_list = pd.DataFrame(connections_list, columns=["from_stop", "to_stop", "dep_time", "arrival_time", "trip_id"])
    print(" B. Filtering connections...")
    connections_list = connections_list[
        (connections_list.from_stop != connections_list.to_stop) & (connections_list.dep_time != connections_list.arrival_time) & (
                connections_list.dep_time < connections_list.arrival_time)]
    print(f"{ini_len - len(connections_list)} connections removed due to inconsistency")

    print(" C. Sorting connections array...")
    connections_list = connections_list.sort_values(by=["dep_time", 'trip_id']).reset_index(drop=True).reset_index()
    connections_list = connections_list.values.tolist()
    print(breaker)
    return connections_list


def save_csa(final_connections: list, NETWORK_NAME: str) -> None:
    """
    Save structures related to CSA

    Args:
        final_connections (list): list of tuples. format: [(from stop, to stop, from time, to time, trip id)].
        NETWORK_NAME (str): Network name

    Returns:
        None

    """
    print(f"Final connections count: {len(final_connections)}")
    print("Saving connections array...")
    with open(f'./dict_builder/{NETWORK_NAME}/connections_dict_pkl.pkl', 'wb') as pickle_file:
        pickle.dump(final_connections, pickle_file)
    print("CSA preprocessing complete")
    print(breaker)
    return None


if __name__ == "__main__":
    with open(f'parameters_entered.txt', 'rb') as file:
        parameter_files = pickle.load(file)
    BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TRANSFER_PATTERNS_FILES, BUILD_CSA = parameter_files
    # BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TP = 1, "anaheim", 1, 1
    if BUILD_CSA == 1:
        breaker, USE_PARALlEL, CORES, start_time = initialize()

        stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = read_testcase(
            NETWORK_NAME)
        input_list = stoptimes_dict.items()

        print("Building connections array...")
        if USE_PARALlEL != 0:
            with Pool(CORES) as pool:
                connections_list = pool.map(extract_connections, input_list)
        else:
            connections_list = [extract_connections(route_trips) for route_trips in tqdm(input_list)]
        connections_list = [y for x in connections_list for y in x]
        print(f"Extracting time: {round(time() - start_time)} seconds\n{breaker}")

        final_connections = process_csa_array(connections_list)
        del (connections_list)
        save_csa(final_connections, NETWORK_NAME)

        """
        ##################################
        Depreciated functions
        #################################
        
        # connections_list = []
        # for route, trip_list in tqdm(stoptimes_dict.items()):
        #     for tid, trip in enumerate(trip_list):
        #         connections = list(zip(trip[:-1], trip[1:]))
        #         connections_list.extend(
        #             [(from_stop, to_stop, from_time, to_time, f'{route}_{tid}') for ((from_stop, from_time), (to_stop, to_time)) in connections])

        """
