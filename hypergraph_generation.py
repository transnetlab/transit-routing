from tqdm import tqdm

import gtfs_loader
from mislaneous_func import *

get_full_trans(time_limit=60)
full_trans = 1
stops_file, routes_file, trips_file, stop_times_file, transfers_file = gtfs_loader.load_all_db(full_trans)
stops_file.sort_values(by=['stop_id'], inplace=True)
stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict = gtfs_loader.load_all_dict(full_trans)

# check(stops_dict, stoptimes_dict, stop_times_file)
overlap = check_nonoverlap(stoptimes_dict)
for x in overlap:
    stoptimes_dict[x] = []
check_footpath(footpath_dict)

stop_times_file = stop_times_file[~stop_times_file.route.isin(overlap)]
master_stoptimes = pd.merge(stop_times_file, trips_file, on=["trip_id"])
route_groups = master_stoptimes.groupby("route_id")
stops_dict, route_map = {}, {}
temp = 1
for x in set(master_stoptimes['route_id']):
    route_map[x] = temp
    temp = temp + 1

print("building stop dict..")
for r_id, route_db in route_groups:
    trips_db = route_db.groupby("trip_id")
    for _, trip in trips_db:
        trip = trip.sort_values(by=["stop_sequence"])
        stops_dict.update({route_map[r_id]: list(trip.stop_id)})
        break

try:
    route_by_stop_dict
except NameError:
    print("building routes by stop dict..")
    route_by_stop_dict = {}
    for stop in tqdm(stops_file["stop_id"]):
        routes_serving_p = []
        for route_stop_pair in stops_dict.items():
            if stop in route_stop_pair[1]:
                routes_serving_p.append(route_stop_pair[0])
        if len(routes_serving_p) < 2:
            continue
        route_by_stop_dict.update({stop: routes_serving_p})

try:
    hyperedges_dict
except NameError:
    print("building hyperedges..")
    hyperedges_dict = {}
    for edge in tqdm(route_by_stop_dict.values()):
        edge = tuple([int(x) for x in edge])
        if edge in hyperedges_dict.keys():
            hyperedges_dict[edge] = hyperedges_dict[edge] + 1
        else:
            hyperedges_dict[edge] = 1

hyperedge_list = []
for x in hyperedges_dict.items():
    y = list(x[0])
    y.insert(0, x[1])
    hyperedge_list.append(y)
temp_set = set()
for x in hyperedges_dict.keys():
    temp_set = temp_set.union(set(x))
first_line = [len(hyperedge_list), len(temp_set), 1]
hyperedge_list.insert(0, first_line)

# file1 = open(r"C:\Users\Admin\Downloads\hmetis-1.5.3-WIN32\hmetis-1.5.3-WIN32\myfile.txt", "w")
file1 = open(r".\hypergraph\hypergraph.txt", "w")
L = [f'{" ".join(str(y) for y in x)} \n' for x in hyperedge_list]
file1.writelines(L)
file1.close()

###################################################################################################################
import os

part = 4
temp = os.getcwd()
os.chdir('./hypergraph/')
# os.popen(f'shmetis hypergraph.txt {part} 15')
os.popen(f'hmetis hypergraph.txt {part} 15 20 1 1 1 0 0')
# os.popen(f'hmetis hypergraph.txt {part} 15 20 1 1 1 0 0')
# os.chdir(temp)
os.chdir('D:\\prateek\\research\\indivisual\\TB1')

###################################################################################################################
"""generate routes after partition"""
output = pd.read_csv(f'.\hypergraph\hypergraph.txt.part.{part}', header=None)
partitions = len(set(output[0]))
tup = list(route_map.items())
tup.sort(key=lambda x: x[1])
final_out = zip(list(output[0]), [x[0] for x in tup])
final_out = list(final_out)
final_out = pd.DataFrame(final_out, columns=['group', 'route_id'])

tableau_file = pd.DataFrame(columns=['point', 'lat', 'long', 'path_id', 'point_order', 'group'])
master_stoptimes = pd.merge(master_stoptimes, stops_file, on=['stop_id'])
master_stoptimes = pd.merge(master_stoptimes, final_out, on=['route_id'])

master_stoptimes.drop(columns=['trip_id', 'arrival_time', 'route', 'stop_name'], inplace=True)
master_stoptimes.rename(
    columns={'stop_lat': 'lat', 'stop_lon': 'long', 'route_id': 'path_id', 'stop_sequence': 'point_order'},
    inplace=True)
route_groups = master_stoptimes.groupby('path_id')
route_out = pd.DataFrame()
for id, x in tqdm(route_groups):
    temp = x.drop_duplicates(subset='point_order').sort_values(by='point_order')
    route_out = route_out.append(temp)
route_out.to_csv(r"route_out.csv", index=False)
route_out.to_csv(r'.\hypergraph\route_out.csv', index=False)
###################################################################################################################
"""generate cut stops"""
stops_group = route_out.groupby("stop_id")
temp = []
for id, details in stops_group:
    groups = set(details['group'])
    if len(groups) == partitions:
        g_id = 'c'
    else:
        g_id = list(groups)[0]
    temp.append([id, details.lat.iloc[0], details.long.iloc[0], g_id])
temp = pd.DataFrame(temp, columns=['stop_id', 'lat', 'long', 'g_id'])
temp.to_csv(r'cut_stops.csv', index=False)
temp.to_csv(r'.\hypergraph\cut_stops.csv', index=False)
print(f'{len(temp[temp.g_id == "c"]) / len(set(route_out["stop_id"])) * 100}/ are cut stops')
###################################################################################################################
