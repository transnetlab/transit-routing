from timeit import default_timer as timer
from tqdm import tqdm

import gtfs_loader
from TBTR.rTBTR import range_TBTR_main
from dict_builder import stops_dict_builder, stoptimes_dict_builder, route_by_stop_builder, transfer_dict_builder
from miscellaneous_func import *

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

stop_times_file = add_custom_tripid_to_stoptimes(stop_times_file)

SOURCE, DESTINATION = 3, 5
MAX_TRANSFER = 3

# WALKING_FROM_SOURCE = 0
PRINT_PARA = 1
CHANGE_TIME_SEC = 0

cut_stops = pd.read_csv(r"./hypergraph/cut_stops.csv", usecols=['stop_id', 'g_id'])
cut_stops = list(cut_stops[cut_stops.g_id == 'c'].stop_id)
cut_stops = [3, 7, 9]
d_time_list = get_timelist(SOURCE, stop_times_file)
with open('./dict_builder/trip_transfer_dict.pkl', 'rb') as file:
    trip_transfer_dict = pickle.load(file)

trip_set = set(trip_transfer_dict.keys())
start = timer()
for SOURCE in tqdm(cut_stops):break
    fill_in_trips = set()
    d_time_list = get_timelist(SOURCE, stop_times_file)
    for DESTINATION in cut_stops:
        if SOURCE == DESTINATION: continue
        fill_in_trips = fill_in_trips.union(range_TBTR_main(MAX_TRANSFER, SOURCE, DESTINATION, d_time_list, routes_by_stop_dict, stops_dict,
                                        stoptimes_dict,
                                        footpath_dict, trip_transfer_dict, trip_set))
    pd.DataFrame(fill_in_trips).to_csv(f'./{SOURCE}.csv', index=False)
end = timer()
print(f'elapsed time: {end - start}')