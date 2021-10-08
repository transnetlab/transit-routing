"""
Module contains the test case for standard One-To-Many rRAPTOR implementation
"""

from time import process_time as time_measure
import gtfs_loader
from RAPTOR.one_to_many_rraptor import onetomany_rraptor
from miscellaneous_func import *
from dict_builder import dict_builder_functions
print_logo()
print("Reading Testcase...")
FOLDER = './swiss'
get_full_trans(FOLDER, time_limit="full")
stops_file, trips_file, stop_times_file, transfers_file = gtfs_loader.load_all_db(FOLDER)
try:
    stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict = gtfs_loader.load_all_dict(FOLDER)
except FileNotFoundError:
    stops_dict = dict_builder_functions.build_save_stops_dict(stop_times_file, trips_file, FOLDER)
    stoptimes_dict = dict_builder_functions.build_save_stopstimes_dict(stop_times_file, trips_file, FOLDER)
    routes_by_stop_dict = dict_builder_functions.build_save_route_by_stop(stop_times_file, FOLDER)
    footpath_dict = dict_builder_functions.build_save_footpath_dict(transfers_file,  FOLDER)

overlap = check_nonoverlap(stoptimes_dict, stops_dict)
for x in overlap:
    stoptimes_dict[x] = []
check_footpath(footpath_dict)
stop_times_file = stop_times_file[~stop_times_file.route_id.isin(overlap)]

print_network_details(transfers_file, trips_file, stops_file)

FOLDER = './test_case/swiss'
SOURCE= 9260
DESTINATION=[12407]
MAX_TRANSFER= 4
WALKING_FROM_SOURCE= 0
CHANGE_TIME_SEC = 0
PRINT_PARA = 1
OPTIMIZED = 0
D_TIME = -1
print_query_parameters(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER , WALKING_FROM_SOURCE)
d_time_groups = stop_times_file.groupby("stop_id")
print("Optimal journeys are:\n###################################")
start = time_measure()
output = onetomany_rraptor(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA, OPTIMIZED,
        routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict)
if OPTIMIZED==1:
    print(f"Trips required to cover optimal journeys are {output}")
else:
    print(f"Routes required to cover optimal journeys are {output}")
print(f'Time for rraptor: {round((time_measure() - start)*1000)} milliseconds')
