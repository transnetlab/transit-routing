from tqdm import tqdm
from time import time

from TBTR.TBTR_main import TBTR_main
import gtfs_loader
from dict_builder import stops_dict_builder, stoptimes_dict_builder, route_by_stop_builder, transfer_dict_builder
from mislaneous_func import *
from RAPTOR.std_raptor import std_raptor

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

overlap = check_nonoverlap(stoptimes_dict)
for x in overlap:
    stoptimes_dict[x] = []
check_footpath(footpath_dict)

with open('./dict_builder/trip_transfer_dict.pkl', 'rb') as file:
    trip_transfer_dict = pickle.load(file)
###########################################################################################
test_file = pd.read_csv(r"test_file.csv")
test_file['time'] = pd.to_datetime(test_file['time'])
max_transfer = 3

###########################################################################################
#Generate tableau file
stops_file.drop(columns="stop_name",inplace=True)
stops_file.rename(columns={'stop_lat':'source_lat','stop_lon':'source_long'},inplace=True)
temp = pd.merge(stops_file,test_file, left_on='stop_id',right_on='source').drop(columns='stop_id')
stops_file.rename(columns={'source_lat':'desti_lat','source_long':'desti_long'},inplace=True)
temp = pd.merge(stops_file,temp, left_on='stop_id',right_on='destination').drop(columns='stop_id')
db = []
count = 0
for _,test_od in tqdm(temp.iterrows()):
    count = count + 1
    db.append((test_od.source,1, count, test_od.source_lat,test_od.source_long, test_od.time))
    db.append((test_od.destination,2, count, test_od.desti_lat,test_od.desti_long,test_od.time))
pd.DataFrame(db,columns=['stop_id', 'point_order','path_id','lat','long','group']).to_csv(r'test_od_pairs.csv',index=False)

############################################################
'''#Check RAPTOR and TBTR
null_od = 0
for _,test_od in tqdm(test_file.iterrows()):
    rap_out = std_raptor(max_transfer,  test_od.source, test_od.destination, test_od.time , routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source =0 , print_para =0 ,
                     save_routes = 0 , change_time_sec = 0)
    if rap_out == -1:
        null_od = null_od + 1
    TBTR_out = TBTR_main(max_transfer, test_od.source, test_od.destination, test_od.time, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, transfers_file, trip_transfer_dict,
                     walking_from_source = 0, print_para=0)
    if rap_out!=TBTR_out:
        print(test_od)
        print(rap_out)
        print(TBTR_out)
'''
############################################################
print('measuring RAPTOR')
rap_time = 0
for _,test_od in test_file.iterrows():
    s = time()
    std_raptor(max_transfer,  test_od.source, test_od.destination, test_od.time , routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source =0 , print_para =0,
                     save_routes = 0, change_time_sec = 0)
    e = time()
    rap_time = rap_time + (e - s)
print(f'time by RAPTOR is {rap_time/len(test_file)}')

############################################################
print('measuring TBTR')
tbtr_time = 0
for _,test_od in test_file.iterrows():
    s = time()
    TBTR_main(max_transfer, test_od.source, test_od.destination, test_od.time, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, transfers_file, trip_transfer_dict,
                     walking_from_source = 0, print_para=0)
    e = time()
    tbtr_time = tbtr_time + (e - s)
print(f'time by TBTR is {tbtr_time/len(test_file)}')
############################################################