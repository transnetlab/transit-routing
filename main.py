"""
This is the Main module.
"""
from collections import defaultdict

from RAPTOR.std_raptor import raptor
from RAPTOR.rraptor import rraptor
from RAPTOR.one_to_many_rraptor import onetomany_rraptor
from RAPTOR.hypraptor import hypraptor
from TBTR.tbtr import tbtr
from TBTR.rtbtr import rtbtr
from TBTR.one_many_tbtr import onetomany_rtbtr
from TBTR.hyptbtr import hyptbtr
from miscellaneous_func import *

print_logo()
print("Reading Testcase...")


def take_inputs():
    """
    defines the use input
    Returns:
        algorithm (int): algorithm type. 0 for RAPTOR and 1 for TBTR
        variant (int): variant of the algorithm. 0 for normal version,
                                                 1 for range version,
                                                 2 for One-To-Many version,
                                                 3 for Hyper version
    """
    algorithm = int(input("Press 0 for RAPTOR \nPress 1 for TBTR \n"))
    print("***************")
    if algorithm == 0:
        variant = int(input(
            "Press 0 for RAPTOR \nPress 1 for rRAPTOR \nPress 2 for One-To-Many rRAPTOR \nPress 3 for HypRAPTOR \n"))
    elif algorithm == 1:
        variant = int(input("Press 0: TBTR \nPress 1: rTBTR \nPress 2: One-To-Many rTBTR \nPress 3: HypTBTR \n"))
    print("***************")
    return algorithm, variant


def main():
    """
    Runs the test case depending upon the values of algorithm, variant
    """
    algorithm, variant = take_inputs()
    print_query_parameters(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, variant, NO_OF_PARTITIONS=4,
                           WEIGHING_SCHEME="S2", PARTITIONING_ALGORITHM="KaHyPar")
    if algorithm == 0:
        if variant == 0:
            output = raptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA,
                            routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
            print(f"Optimal arrival time are: {output}")
        elif variant == 1:
            output = rraptor(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA,
                             OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 2:
            output = onetomany_rraptor(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC,
                                       PRINT_PARA, OPTIMIZED,
                                       routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 3:
            output = hypraptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA,
                               stop_out, route_groups, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
            print(f"Optimal arrival time are: {output}")
    if algorithm == 1:
        if variant == 0:
            output = tbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA, routes_by_stop_dict, stops_dict, stoptimes_dict,
                          footpath_dict, trip_transfer_dict, trip_set)
            print(f"Optimal arrival times are: {output[0]}")
        elif variant == 1:
            output = rtbtr(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA, OPTIMIZED,
                           routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, trip_transfer_dict, trip_set)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 2:
            output = onetomany_rtbtr(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA,
                                     OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, trip_transfer_dict, trip_set)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 3:
            output = hyptbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA, stop_out, trip_groups,
                             routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, trip_transfer_dict, trip_set)
            print(f"Optimal arrival times are: {output[0]}")


if __name__ == "__main__":
    # Read network
    FOLDER = './swiss'
    stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict = read_testcase()
    with open(f'./GTFS/{FOLDER}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
        trip_transfer_dict = pickle.load(file)
    trip_set = set(trip_transfer_dict.keys())
    for tid, connnections in trip_transfer_dict.items():
        deaf = defaultdict(lambda: [])
        deaf.update(connnections)
        trip_transfer_dict[tid] = deaf
    print_network_details(transfers_file, trips_file, stops_file)

    # Query parameters
    SOURCE = 9865
    DESTINATION = 12683
    DESTINATION_LIST = [12683]
    D_TIME = stop_times_file.arrival_time.sort_values().iloc[0]
    MAX_TRANSFER = 4
    WALKING_FROM_SOURCE = 0
    CHANGE_TIME_SEC = 0
    PRINT_PARA = 0
    OPTIMIZED = 1
    stop_out, route_groups, _, trip_groups = read_partitions_new(stop_times_file, FOLDER, no_of_partitions=4, weighting_scheme="S2", partitioning_algorithm="kahypar")

    # main function
    d_time_groups = stop_times_file.groupby("stop_id")
    main()
