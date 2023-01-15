from time import time as time_measure
from tqdm import tqdm
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
    print_query_parameters(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, variant, no_of_partitions=4,
                           weighting_scheme="S6", partitioning_algorithm="KaHyPar")
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
            output = onetomany_rraptor(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC,
                                       PRINT_ITINERARY, OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
            if OPTIMIZED == 1:
                print(f"Trips required to cover optimal journeys are {output}")
            else:
                print(f"Routes required to cover optimal journeys are {output}")
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


if __name__ == "__main__":
    # Read network
    FOLDER = './swiss'  #Done
    FOLDER = './nl'
    FOLDER = './uk'
    FOLDER = './israel'
    FOLDER = './taiwan'
    FOLDER = './germany'
    FOLDER = './sweden'
    FOLDER = './bangalore'
    FOLDER = './anaheim'
    print(FOLDER)

    stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict = read_testcase(
        FOLDER)

    with open(f'./GTFS/{FOLDER}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
        trip_transfer_dict = pickle.load(file)
    trip_set = set(trip_transfer_dict.keys())
    print_network_details(transfers_file, trips_file, stops_file)
    random_od = pd.read_csv(f"./GTFS/{FOLDER}_randomOD.csv", nrows=3000)
    # Query parameters
    D_TIME = stop_times_file.arrival_time.sort_values().iloc[0]
    MAX_TRANSFER = 4
    WALKING_FROM_SOURCE = 1
    CHANGE_TIME_SEC = 0
    PRINT_ITINERARY = 1
    OPTIMIZED = 1
    # stop_out, route_groups, _, trip_groups = read_partitions(stop_times_file, FOLDER, no_of_partitions=4, weighting_scheme="S6",
    #                                                          partitioning_algorithm="kahypar")
    # nested_stop_out, nested_route_groups, _, nested_trip_groups = read_nested_partitions(stop_times_file, FOLDER, no_of_partitions=4, weighting_scheme="S6")
    d_time_groups = stop_times_file.groupby("stop_id")
    time_list = []
    SOURCE, DESTINATION = 38, 52
    output = raptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY,
                    routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)

    for _, row in tqdm(random_od.iterrows()):break
        SOURCE, DESTINATION = row.SOURCE, row.DESTINATION
        start = time_measure()
        output = raptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_ITINERARY,
                        routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)
        output[1]
        end = round((time_measure() - start)*1000,3)
        time_list.append((SOURCE, DESTINATION, end))
    time_list_db = pd.DataFrame(time_list, columns=["SOURCE", "DESTINATION", "Time (ms)"])
    time_list_db.to_csv(f"./runtimes/{FOLDER[2:]}/raptor_runtime_{FOLDER[2:]}.csv", index=False)
    print(f'Mean runtime: {time_list_db["Time (ms)"].mean()} ms')

