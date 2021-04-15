from time import time
from tqdm import tqdm
import gtfs_loader
from RAPTOR.std_raptor import std_raptor
from TBTR.TBTR_main import TBTR_main
from dict_builder import stops_dict_builder, stoptimes_dict_builder, route_by_stop_builder, transfer_dict_builder
from mislaneous_func import *

get_full_trans(time_limit=60)
full_trans = 1
stops_file, routes_file, trips_file, stop_times_file, transfers_file = gtfs_loader.load_all_db(full_trans)
stops_file.sort_values(by=['stop_id'], inplace=True)
try:
    stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict = gtfs_loader.load_all_dict(full_trans)
except FileNotFoundError:
    stops_dict = stops_dict_builder.build_save_stops_dict(stop_times_file, trips_file)
    stoptimes_dict = stoptimes_dict_builder.build_save_stopstimes_dict(stop_times_file, trips_file)
    routes_by_stop_dict = route_by_stop_builder.build_save_route_by_stop(stops_dict, stops_file)
    footpath_dict = transfer_dict_builder.build_save_footpath_dict(transfers_file, full_trans)

# check(stops_dict, stoptimes_dict, stop_times_file)
overlap = check_nonoverlap(stoptimes_dict)
for x in overlap:
    stoptimes_dict[x] = []
check_footpath(footpath_dict)

build = 0
if build == 1:
    from TBTR import algo1, algo2, algo3

    start1 = time()
    algo1.build_transfer_set(stoptimes_dict, footpath_dict, routes_by_stop_dict, stops_dict, para=1, change_time=0)
    t1 = int(time() - start1) / 60
    start2 = time()
    algo2.remove_Uturns(stoptimes_dict)
    t3 = int(time() - start2) / 60
    start3 = time()
    algo3.optiaml_trans(stoptimes_dict, footpath_dict)
    t2 = int(time() - start3) / 60
    print(f"time taken is {(int(time() - start1) / 60)}----{({t1}, {t2}, {t3})}")

######################################################main################################################################################################
with open('./dict_builder/trip_transfer_dict.pkl', 'rb') as file:
    trip_transfer_dict = pickle.load(file)

trip_set = set(trip_transfer_dict.keys())

'''print("started")
from random import choice
walking_from_source=0
save_routes, change_time_sec = 0, 0
print_para=1
count = 0
while True:
    count = count + 1
    source = choice(list(routes_by_stop_dict.keys()))
    destination = choice(list(routes_by_stop_dict.keys()))
    if source == destination: continue
    source, destination =  3 ,5
    d_time, max_transfer = pd.to_datetime(f'2019-10-03 06:06:00'), 3
    rap_out = std_raptor(max_transfer, source, destination, d_time,
                         routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source, print_para,
                         save_routes, change_time_sec)
    TBTR_out = TBTR_main(max_transfer,source, destination, d_time, routes_by_stop_dict, stops_dict, stoptimes_dict,
                              footpath_dict,trip_transfer_dict, walking_from_source, print_para, trip_set)
    if not rap_out == TBTR_out:
        print("error output", source, destination)
        print(rap_out)
        print(TBTR_out)
    if count%500==0:
        print(count)
'''
nrows=1100
test = pd.read_csv(r'test_file.csv',nrows=nrows)
test['time'] = pd.to_datetime(test['time'])
walking_from_source, print_para = 0, 0
change_time_sec = 0
save_routes = 0
d_time, max_transfer = pd.to_datetime(f'2019-10-03 06:06:00'), 3

rap_time  = 0
TBTR_time  = 0
for _,row in tqdm(test.iterrows()):
    s = time()
    a = std_raptor(max_transfer, row.source, row.destination, row.time,
                         routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source, print_para,
                         save_routes, change_time_sec)
    rap_time = rap_time + time()- s
    s = time()
    b = TBTR_main(max_transfer,row.source, row.destination, row.time, routes_by_stop_dict, stops_dict, stoptimes_dict,
                              footpath_dict,trip_transfer_dict, walking_from_source, print_para, trip_set)

    TBTR_time = TBTR_time + time()- s
    if a==b:
        pass
    else:print("output error")
print(f'RAPTOR {rap_time/len(test)}')
print(f'TBTR {TBTR_time/len(test)}')
source, destination, d_time = row.source, row.destination, row.time
#########################################################################################################
'''rap_time  = 0
TBTR_time  = 0
from RAPTOR.temp_raptor import new_raptor
for _,row in tqdm(test.iterrows()):
    s = time()
    a = std_raptor(max_transfer, row.source, row.destination, row.time,
                         routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source, print_para,
                         save_routes, change_time_sec)
    rap_time = rap_time + time()- s
#    s = time()
#    b = new_raptor(max_transfer, row.source, row.destination, row.time,
#                         routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source, print_para,
#                         save_routes, change_time_sec)
#    b = new_raptor(max_transfer,row.source, row.destination, row.time, routes_by_stop_dict, stops_dict, stoptimes_dict,
#                              footpath_dict,trip_transfer_dict, walking_from_source, print_para, trip_set)

#    TBTR_time = TBTR_time + time()- s
#    if a==b:
#        pass
#    else:print("output error")
print(f'RAPTOR {rap_time/len(test)}')
#print(f'TBTR {TBTR_time/len(test)}')
source, destination, d_time = row.source, row.destination, row.time

'''