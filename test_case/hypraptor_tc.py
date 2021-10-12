"""
Module contains the test case for HypRAPTOR implementation
"""
from time import process_time as time_measure

import gtfs_loader
from RAPTOR.hypraptor import hypraptor
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
print_network_details(transfers_file, trips_file, stops_file)
########################################
SOURCE = 9260
DESTINATION = 12407
D_TIME = stop_times_file.arrival_time.sort_values().iloc[0]
MAX_TRANSFER = 4
WALKING_FROM_SOURCE = 0
CHANGE_TIME_SEC = 0
PRINT_PARA = 1
NO_OF_PARTITIONS = 4
WEIGHING_SCHEME = "S2"
PARTITIONING_ALGORITHM = "kahypar"
print_query_parameters(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, NO_OF_PARTITIONS,
                       WEIGHING_SCHEME, PARTITIONING_ALGORITHM)
########################################
stop_out, route_groups, _, _ = read_partitions_new(stop_times_file, FOLDER, part=NO_OF_PARTITIONS,
                                                   scheme=WEIGHING_SCHEME, algo=PARTITIONING_ALGORITHM)
print("Optimal journeys are:\n###################################")
start = time_measure()
output = hypraptor(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA,
                   stop_out, route_groups, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
print(f'Time for hypraptor: {round((time_measure() - start) * 1000)} milliseconds')
########################################
