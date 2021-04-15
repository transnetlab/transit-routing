import gtfs_loader
from dict_builder import stops_dict_builder, stoptimes_dict_builder, route_by_stop_builder, transfer_dict_builder
from mislaneous_func import *
from RAPTOR.rRAPTOR import rraptor_main
from tqdm import tqdm
from RAPTOR.fill_in_mannual_raptor import fill_in_rap

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
stop_times_file = stop_times_file[~stop_times_file.route.isin(overlap)]

def add_custom_tripid_to_stoptimes(stop_times_file):
    import pandas as pd
    stop_times_file.arrival_time = pd.to_datetime(stop_times_file.arrival_time)
    route_trips = stop_times_file.groupby("route")
    temp = {}
    for r,trips in route_trips:
        temp1 = enumerate(list(trips[trips.stop_sequence==0].sort_values(by=['arrival_time'])['trip_id']))
        temp.update({x[1]:f'{r}_{x[0]}' for x in temp1})
    temp = pd.DataFrame(temp.items(),columns=['trip_id','trip_id_new'])
    return  pd.merge(stop_times_file , temp, on=['trip_id']).drop(columns=['trip_id']).rename(columns = {'trip_id_new':'trip_id'})

stop_times_file = add_custom_tripid_to_stoptimes(stop_times_file)

def get_timelist(source, stop_times_file):
    d_time_groups = stop_times_file.groupby('stop_id')
    d_time_list = list(zip(d_time_groups.get_group(source)["trip_id"], d_time_groups.get_group(source)['arrival_time'],
                           d_time_groups.get_group(source)['stop_sequence']))
    d_time_list.sort(key=lambda x: x[1],reverse=True)
    return d_time_list

source, destination = 3, 5
max_transfer = 3

walking_from_source = 0
print_para = 1
change_time_sec = 0
#for d_time in d_time_list:
#    fill_in_rap(max_transfer, source, destination, d_time, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source = 0 , print_para = 1, save_routes =0 , change_time_sec = 0)

cut_stops = pd.read_csv(r"./hypergraph/cut_stops.csv",usecols=['stop_id','g_id'])
cut_stops = list(cut_stops[cut_stops.g_id=='c'].stop_id)


for source in tqdm(cut_stops):
    for destination in cut_stops:
        if source==destination:continue
        d_time_list = get_timelist(source, stop_times_file)
        fill_in_trips = set(rraptor_main(max_transfer, source, destination,d_time_list, routes_by_stop_dict, stops_dict,
                                         stoptimes_dict, footpath_dict, print_para = 1, change_time_sec = 0, optimized= 0))
    pd.DataFrame(fill_in_trips).to_csv(r'./fill_in/source.csv',index=False)


