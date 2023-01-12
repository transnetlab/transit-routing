"""
Builds structures related to transfer patterns
"""
import glob
import multiprocessing
import os
import pickle
import sys
from multiprocessing import Pool
from random import shuffle
from time import time

from tqdm import tqdm

from TRANSFER_PATTERNS.transferpattern_func import *
from miscellaneous_func import *


def run_tbtr(SOURCE) -> None:
    """
    Generate transfer patterns in parallel using TBTR. Transfer patterns are saved locally.

    Args:
        SOURCE (int): stop id of source stop.

    Returns:
        None

    """
    DESTINATION_LIST = list(routes_by_stop_dict.keys())
    # print(SOURCE, psutil.Process().cpu_num())
    output = onetomany_rtbtr_forhubs(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY,
                                     OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict,
                                     trip_set, hubstops)
    with open(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_{HUB_COUNT}/{SOURCE}", "wb") as fp:
        pickle.dump(output, fp)
    return None


def run_raptor(SOURCE):
    """
    Generate transfer patterns in parallel using RAPTOR. Transfer patterns are saved locally.

    Args:
        SOURCE (int): stop id of source stop.

    Returns:
        None

    """
    DESTINATION_LIST = list(routes_by_stop_dict.keys())
    # print(SOURCE, psutil.Process().cpu_num())
    output = onetoall_rraptor_forhubs(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC,
                                      PRINT_ITINERARY, OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict,
                                      footpath_dict, idx_by_route_stop_dict, hubstops)
    with open(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_{HUB_COUNT}/{SOURCE}", "wb") as fp:
        pickle.dump(output, fp)
    return None


def initialize() -> tuple:
    """
    Initialize variables for building transfer patterns file.

    Returns:
        breaker (str): print line breaker
        G: Network graph of NETWORK NAME
        stops_list (list):
        CORES (int): Number of codes to be used
        WALKING_LIMIT (int): Maximum allowed walking time
        start_time: timestamp object
        USE_PARALlEL (int): 1 for parallel and 0 for serial
        MAX_TRANSFER (int): maximum transfer limit for which transfer patterns will be built.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 indicates walking from SOURCE is allowed.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.
        GENERATE_LOGFILE (int): 1 to redirect and save a log file. Else 0
        USE_TBTR (int): 1 to use TBTR for generating transfer patterns. 0 for RAPTOR
        CHANGE_TIME_SEC (int): change-time in seconds.

    """
    breaker = "________________________________________________________________"
    print(breaker)
    print("Building transfer patterns file. Enter following parameters.\n")
    USE_PARALlEL = int(input("Transfer patterns.txt can be built in parallel. Enter 1 to use multiprocessing. Else press 0. Example: 0\n: "))
    CORES = 0
    if USE_PARALlEL != 0:
        CORES = int(input(f"Enter number of CORES (>=1). \nAvailable CORES (logical and physical):  {multiprocessing.cpu_count()}\n: "))
    import psutil
    print(f'RAM {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB (% used:{psutil.virtual_memory()[2]})')
    start_time = time()
    HUB_COUNT = int(input("Enter the number of hub stops. Else press 0. Example: 0\n: "))
    MAX_TRANSFER = int(input("Enter maximum transfer limit for which transfer patterns would be built. Example: 4\n: "))
    WALKING_FROM_SOURCE = int(input("Press 1 to allow walking from source stop else press 0. Example: 1\n: "))
    GENERATE_LOGFILE = int(input("Press 1 to generate logfile else press 0. Example: 0\n: "))
    if GENERATE_LOGFILE == 1:
        print("All outputs will be redirected to log file")
    USE_TBTR = int(input("Press 1 to use TBTR to build Transfer Patterns.\nPress 2 to use RAPTOR to build Transfer Patterns. Example: 2\n: "))
    PRINT_ITINERARY = 0
    OPTIMIZED = 1
    CHANGE_TIME_SEC = 0
    return breaker, CORES, start_time, USE_PARALlEL, HUB_COUNT, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY, OPTIMIZED, GENERATE_LOGFILE, USE_TBTR, CHANGE_TIME_SEC


def remove_older_files(NETWORK_NAME, HUB_COUNT) -> None:
    """
    Creates a new (empty) directory for saving transfer patterns.

    Args:
        NETWORK_NAME (str): GTFS path
        HUB_COUNT (int):  Number of hub stops

    Returns:
        None

    """
    if not os.path.exists(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_{HUB_COUNT}/."):
        os.makedirs(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_{HUB_COUNT}/.")
    files = glob.glob(f'./TRANSFER_PATTERNS/{NETWORK_NAME}_{HUB_COUNT}/*')
    if files != []:
        print(f"Cleaning existing files (if any) in directory ./TRANSFER_PATTERNS/transfer_pattern/{NETWORK_NAME}_{HUB_COUNT}/")
        for f in files:
            os.remove(f)
    return None


def post_process(runtime, CORES, HUB_COUNT, NETWORK_NAME) -> None:
    """
    Post process and print the statistics realted to transfer patterns.

    Args:
        runtime (float): total runtime in minutes
        CORES (int): Number of codes to be used
        HUB_COUNT (int):  number of hub stops
        NETWORK_NAME (str): GTFS path

    Returns:
        None

    """
    Folderpath = f'./TRANSFER_PATTERNS/{NETWORK_NAME}_{HUB_COUNT}'
    total_kb_list = [os.path.getsize(ele) for ele in os.scandir(Folderpath)]
    file_count = len(total_kb_list)
    total_kb = sum(total_kb_list)
    Gb_size = total_kb / (1024 ** 3)
    MB_size = total_kb / (1024 ** 2)
    print(breaker)
    print(f'Time required: {runtime} minutes')
    print(f'CORES USED: {CORES}')
    print(f'HUB_COUNT: {HUB_COUNT}')
    print(f'Space: {round(Gb_size, 2)} GB ({round(MB_size, 2)} MB)')
    print(f'Total files saved: {file_count}')
    print("Transfer Patterns preprocessing complete")
    print(breaker)
    return None


if __name__ == "__main__":
    with open(f'parameters_entered.txt', 'rb') as file:
        parameter_files = pickle.load(file)
    BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TRANSFER_PATTERNS_FILES, BUILD_CSA = parameter_files
    # BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TP = 1, "anaheim", 1, 1
    if BUILD_TRANSFER_PATTERNS_FILES == 1:
        breaker, CORES, start_time, USE_PARALlEL, HUB_COUNT, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY, OPTIMIZED, GENERATE_LOGFILE, USE_TBTR, CHANGE_TIME_SEC = initialize()
        print(breaker)
        stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = read_testcase(
            NETWORK_NAME)
        print_network_details(transfers_file, trips_file, stops_file)
        if GENERATE_LOGFILE == 1:
            if not os.path.exists(f'./logs/.'):
                os.makedirs(f'./logs/.')
            sys.stdout = open(f'./logs/transfer_patterns_{NETWORK_NAME[2:]}_{HUB_COUNT}', 'w')
        print(f"Network: {NETWORK_NAME}")
        print(f'CORES used ={CORES}')
        print(breaker)
        # Import Hub information
        hubs_dict = {}
        if HUB_COUNT != 0:
            method = "brute"
            with open(f'./TRANSFER_PATTERNS/{NETWORK_NAME}_hub_{method}.pkl', 'rb') as file:
                hubs_dict = pickle.load(file)
        hubs_dict[0] = []
        hubstops = hubs_dict[HUB_COUNT]
        remove_older_files(NETWORK_NAME, HUB_COUNT)
        # Main code
        source_LIST = list(routes_by_stop_dict.keys())
        # source_LIST = source_LIST[:50]
        shuffle(source_LIST)
        d_time_groups = stop_times_file.groupby("stop_id")
        print("Generating transfer patterns...")
        if USE_TBTR == 1:
            try:
                with open(f'./GTFS/{NETWORK_NAME}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
                    trip_transfer_dict = pickle.load(file)
                trip_set = set(trip_transfer_dict.keys())
            except FileNotFoundError:
                print("TBTR files not found. Either build TBTR or reinitialize using RAPTOR")
            if USE_PARALlEL == 1:
                with Pool(CORES) as pool:
                    result = pool.map(run_tbtr, source_LIST)
                runtime = round((time() - start_time) / 60, 1)
            else:
                result = [run_tbtr(source) for source in tqdm(source_LIST)]
                runtime = round((time() - start_time) / 60, 1)
        else:
            if USE_PARALlEL == 1:
                with Pool(CORES) as pool:
                    result = pool.map(run_raptor, source_LIST)
                runtime = round((time() - start_time) / 60, 1)
            else:
                # source = 36
                result = [run_raptor(source) for source in tqdm(source_LIST)]
                runtime = round((time() - start_time) / 60, 1)
        post_process(runtime, CORES, HUB_COUNT, NETWORK_NAME)

        sys.stdout.close()
