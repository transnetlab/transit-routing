"""
Runs the query algorithm
"""

from RAPTOR.hypraptor import hypraptor
# from RAPTOR.one_to_many_rraptor import onetomany_rraptor
from RAPTOR.rraptor import rraptor
from RAPTOR.std_raptor import raptor
from TBTR.hyptbtr import hyptbtr
from TBTR.one_many_tbtr import onetomany_rtbtr
from TBTR.rtbtr import rtbtr
from TBTR.tbtr import tbtr
from TRANSFER_PATTERNS.transferpattens import std_tp
from miscellaneous_func import *
from CSA.std_csa import std_csa
print_logo()


def take_inputs() -> tuple:
    """
    defines the use input

    Returns:
        algorithm (int): algorithm type. 0 for RAPTOR, 1 for TBTR, 2 for Transfer Patterns
        variant (int): variant of the algorithm. 0 for normal version,
                                                 1 for range version,
                                                 2 for One-To-Many version,
                                                 3 for Hyper version
                                                 3 for Nested Hyper version
    """
    algorithm = int(input("Press 0 to enter RAPTOR environment \nPress 1 to enter TBTR environment\nPress 2 to enter Transfer Patterns environment\nPress 3 to enter CSA environment\n: "))
    variant = 0
    print("***************")
    if algorithm == 0:
        variant = int(input(
            "Press 0 for RAPTOR \nPress 1 for rRAPTOR \nPress 2 for One-To-Many rRAPTOR \nPress 3 for HypRAPTOR\nPress 4 for Multilevel-HypRAPTOR\n: "))
    elif algorithm == 1:
        variant = int(input("Press 0: TBTR \nPress 1: rTBTR \nPress 2: One-To-Many rTBTR \nPress 3: HypTBTR \nPress 4 for Multilevel-HypTBTR \n: "))
    print("***************")
    return algorithm, variant


def main() -> None:
    """
    Runs the test case depending upon the values of algorithm, variant
    """
    algorithm, variant = take_inputs()
    print_query_parameters(NETWORK_NAME, SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, variant, no_of_partitions=4,
                           weighting_scheme="S2", partitioning_algorithm="KaHyPar")
    if algorithm == 0:
        if variant == 0:
            output = raptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY,
                            routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
            print(f"Optimal arrival time are: {output}")
        elif variant == 1:
            output = rraptor(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY,
                             OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 2:
            pass
            # output = onetomany_rraptor(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY, OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
            # if OPTIMIZED == 1:
            #     print(f"Trips required to cover optimal journeys are {output}")
            # else:
            #     print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 3:
            output = hypraptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY,
                               stop_out, route_groups, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
            print(f"Optimal arrival time are: {output}")
        elif variant == 4:
            output = hypraptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY,
                               nested_stop_out, nested_route_groups, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
            print(f"Optimal arrival time are: {output}")
    if algorithm == 1:
        if variant == 0:
            output = tbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY, routes_by_stop_dict, stops_dict, stoptimes_dict,
                          footpath_dict, idx_by_route_stop_dict, trip_transfer_dict, trip_set)
            print(f"Optimal arrival times are: {output[0]}")
        elif variant == 1:
            output = rtbtr(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY, OPTIMIZED,
                           routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict, trip_set)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 2:
            output = onetomany_rtbtr(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY,
                                     OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict,
                                     trip_set)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
        elif variant == 3:
            output = hyptbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY, stop_out, trip_groups,
                             routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict, trip_set)
            print(f"Optimal arrival times are: {output[0]}")
        elif variant == 4:
            output = hyptbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_ITINERARY, nested_stop_out, nested_trip_groups,
                             routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict, trip_set)
            print(f"Optimal arrival times are: {output[0]}")
    if algorithm == 2:
        if variant == 0:
            output = std_tp(SOURCE, DESTINATION, D_TIME, footpath_dict, NETWORK_NAME, routesindx_by_stop_dict, stoptimes_dict, hub_count, hubstops)
            print(f"Optimal arrival times are: {output}")
    if algorithm == 3:
        if variant == 0:
            output = std_csa(SOURCE, DESTINATION, D_TIME, connections_list, WALKING_FROM_SOURCE, footpath_dict, PRINT_ITINERARY)
            print(f"Optimal arrival times is: {output}")
    return None


if __name__ == "__main__":
    # Read network
    USE_TESTCASE = int(input("Press 1 to use test case (anaheim), 0 to enter values manually. Example: 1\n: "))
    if USE_TESTCASE == 1:
        NETWORK_NAME = './anaheim'

        stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = read_testcase(
            NETWORK_NAME)

        #Load TBTR files
        try:
            with open(f'./GTFS/{NETWORK_NAME}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
                trip_transfer_dict = pickle.load(file)
            trip_set = set(trip_transfer_dict.keys())
        except FileNotFoundError:
            print("TBTR preprocessing missing")

        #Load CSA files
        try:
            with open(f'./dict_builder/{NETWORK_NAME}/connections_dict_pkl.pkl', 'rb') as file:
                connections_list = pickle.load(file)
        except FileNotFoundError:
            print("CSA preprocessing missing")

        print_network_details(transfers_file, trips_file, stops_file)

        # Query parameters
        SOURCE, DESTINATION, DESTINATION_LIST = 36, 52, [52, 43]
        D_TIME = stop_times_file.arrival_time.sort_values().iloc[0]
        MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC = 4, 1, 0
        hub_count, hubstops = 0, set()

        PRINT_ITINERARY, OPTIMIZED = 1, 0
        # TODO add partition testcases

        # stop_out, route_groups, _, trip_groups = read_partitions(stop_times_file, NETWORK_NAME, no_of_partitions=4, weighting_scheme="S2", partitioning_algorithm="kahypar")
        # nested_stop_out, nested_route_groups, _, nested_trip_groups = read_nested_partitions(stop_times_file, NETWORK_NAME, no_of_partitions=4, weighting_scheme="S2")

    else:
        NETWORK_NAME = input("Enter Network name in small case. Example: anaheim\n: ")

        stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = read_testcase(
            NETWORK_NAME)

        #Load TBTR files
        try:
            with open(f'./GTFS/{NETWORK_NAME}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
                trip_transfer_dict = pickle.load(file)
            trip_set = set(trip_transfer_dict.keys())
        except FileNotFoundError:
            print("TBTR preprocessing missing")

        #Load CSA files
        try:
            with open(f'./dict_builder/{NETWORK_NAME}/connections_dict_pkl.pkl', 'rb') as file:
                connections_list = pickle.load(file)
        except FileNotFoundError:
            print("CSA preprocessing missing")
        print_network_details(transfers_file, trips_file, stops_file)

        SOURCE = int(input("Enter source stop id\n: "))
        DESTINATION = int(input("Enter destination stop id\n: "))
        D_TIME = pd.to_datetime(input("Enter departure time. Format: YYYY-MM-DD HH:MM:SS (24 hour format)\n: "))
        MAX_TRANSFER = int(input("Maximum transfer limit\n: "))
        WALKING_FROM_SOURCE = int(input("Press 1 to allow walking from source, else 0\n: "))
        CHANGE_TIME_SEC = int(input("Enter change time (in seconds) \n: "))
        PRINT_ITINERARY, OPTIMIZED = 1, 0
        PARTITIONING_PARAMETER = int(input("Press 1 to enter partitioning related parameters. Else press 0\n: "))
        if PARTITIONING_PARAMETER == 1:
            NO_OF_PARTITION = int(input("Enter number of partitions\n: "))
            WEIGHING_SCHEME = str(input("Enter weighing scheme [S1, S2, S3 S4 S5 S6]\n: "))

            stop_out, route_groups, _, trip_groups = read_partitions(stop_times_file, NETWORK_NAME, no_of_partitions=NO_OF_PARTITION,
                                                                     weighting_scheme=WEIGHING_SCHEME, partitioning_algorithm="kahypar")
            nested_stop_out, nested_route_groups, _, nested_trip_groups = read_nested_partitions(stop_times_file, NETWORK_NAME,
                                                                                                 no_of_partitions=NO_OF_PARTITION,
                                                                                                 weighting_scheme=WEIGHING_SCHEME)

    # main function
    d_time_groups = stop_times_file.groupby("stop_id")
    main()
