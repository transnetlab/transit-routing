"""
Module contains the test case for HypTBTR implementation
"""
from collections import defaultdict
from time import process_time as time_measure

import gtfs_loader
from TBTR.hyptbtr import hyptbtr
from dict_builder import dict_builder_functions
from miscellaneous_func import *

print_logo()
########################################
print("Reading Testcase...")
FOLDER = './swiss'
stops_file, trips_file, stop_times_file, transfers_file = gtfs_loader.load_all_db(FOLDER)
try:
    stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict = gtfs_loader.load_all_dict(FOLDER)
except FileNotFoundError:
    stops_dict = dict_builder_functions.build_save_stops_dict(stop_times_file, trips_file, FOLDER)
    stoptimes_dict = dict_builder_functions.build_save_stopstimes_dict(stop_times_file, trips_file, FOLDER)
    routes_by_stop_dict = dict_builder_functions.build_save_route_by_stop(stop_times_file, FOLDER)
    footpath_dict = dict_builder_functions.build_save_footpath_dict(transfers_file, FOLDER)
with open(f'./GTFS/{FOLDER}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
    trip_transfer_dict = pickle.load(file)

trip_set = set(trip_transfer_dict.keys())
for tid, connnections in trip_transfer_dict.items():
    deaf = defaultdict(lambda: [])
    deaf.update(connnections)
    trip_transfer_dict[tid] = deaf
print_network_details(transfers_file, trips_file, stops_file)
########################################
SOURCE = 9865
DESTINATION = 12683
D_TIME = stop_times_file.arrival_time.sort_values().iloc[0]
MAX_TRANSFER = 4
WALKING_FROM_SOURCE = 0
CHANGE_TIME_SEC = 0
PRINT_PARA = 0
NO_OF_PARTITIONS = 4
WEIGHING_SCHEME = "S2"
PARTITIONING_ALGORITHM = "kahypar"
print_query_parameters(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, NO_OF_PARTITIONS,
                       WEIGHING_SCHEME, PARTITIONING_ALGORITHM)
########################################
stop_out, _, _, trip_groups = read_partitions_new(stop_times_file, FOLDER, part=NO_OF_PARTITIONS,
                                                   scheme=WEIGHING_SCHEME, algo=PARTITIONING_ALGORITHM)
start = time_measure()
output = hyptbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA, stop_out, trip_groups,
                 routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, trip_transfer_dict, trip_set)
print(f"Optimal arrival times are: {output[0]}")
print(f'Time for hyptbtr: {round((time_measure() - start) * 1000)} milliseconds')
########################################
