"""
Module contains the test case for rRAPTOR implementation
"""
from time import process_time as time_measure

import gtfs_loader
from RAPTOR.rraptor import rraptor
from dict_builder import dict_builder_functions
from miscellaneous_func import *

print_logo()
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
SOURCE = 9865
DESTINATION = 12683
MAX_TRANSFER = 4
WALKING_FROM_SOURCE = 0
CHANGE_TIME_SEC = 0
PRINT_PARA = 1
OPTIMIZED = 1
D_TIME = -1
print_query_parameters(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE)
########################################
d_time_groups = stop_times_file.groupby("stop_id")
print("Optimal journeys are:\n###################################")
start = time_measure()
output = rraptor(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA,
                 OPTIMIZED, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
if OPTIMIZED == 1:
    print(f"Trips required to cover optimal journeys are {output}")
else:
    print(f"Routes required to cover optimal journeys are {output}")
print(f'Time for rraptor: {round((time_measure() - start) * 1000)} milliseconds')
########################################
