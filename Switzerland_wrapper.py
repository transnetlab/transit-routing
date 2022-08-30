"""
Apply necessary filters to GTFS set. Note that this file is GTFS-specific.
"""
import pandas as pd
from tqdm import tqdm
import numpy as np
import networkx as nx

# Specify paths
path = './swiss'    # Path to unzipped GTFS set
save_path = f'./GTFS/{path.split("/")[1]}'

# Remove unwanted route categories
route = pd.read_csv(f'{path}/gtfs_o/routes.txt')
valid_route_types = list(set(route.route_type))
route.route_type.value_counts()
unwanted_route = [2, 401, 1501, 1300, 900, 1000, 7, 1300]
valid_route_types = [x for x in valid_route_types if x not in unwanted_route]
route = route[route.route_type.isin(valid_route_types)]
valid_routes = set(route.route_id)

# Filter trips and routes based on Calendar dates
date = 20190610
calendar_dates = pd.read_csv(f'{path}/gtfs_o/calendar_dates.txt')
calendar_dates.sort_values(by='date', inplace=True)
calendar_dates[(calendar_dates.exception_type == 1)].groupby('date').count().sort_values('service_id')
valid_service_id = set(
    calendar_dates[(calendar_dates.date == date) & (calendar_dates.exception_type == 1)]['service_id'])
trips = pd.read_csv(f'{path}/gtfs_o/trips.txt')
trips = trips[trips.service_id.isin(valid_service_id) & trips.route_id.isin(valid_routes)]
valid_trips = set(trips.trip_id)
valid_route = set(trips.route_id)
print(len(valid_trips), len(valid_route))

# Filter stoptimes file
stop_times = pd.read_csv(f'{path}/gtfs_o/stop_times.txt')
stop_times.stop_sequence = stop_times.stop_sequence - 1
stop_times.stop_id = stop_times.stop_id.astype(str)
stop_times = stop_times[
    (stop_times.trip_id.isin(valid_trips)) & (stop_times.pickup_type == 0) & (stop_times.drop_off_type == 0)]
stop_times['stop_sequence'] = stop_times.groupby("trip_id")["stop_sequence"].rank(method="first",
                                                                                  ascending=True).astype(int) - 1
stop_times = pd.merge(stop_times, trips, on='trip_id')
stops_map = pd.DataFrame([t[::-1] for t in enumerate(set(stop_times.stop_id), 1)], columns=['stop_id', 'new_stop_id'])
stop_times = pd.merge(stop_times, stops_map, on='stop_id').drop(columns=['stop_id', 'departure_time', 'pickup_type',
                                                                         'drop_off_type', 'direction_id',
                                                                         'trip_headsign', 'trip_short_name',
                                                                         'service_id']).rename(columns={'new_stop_id': 'stop_id'})
date = f'{str(date)[:4]}-{str(date)[4:6]}-{str(date)[6:]}'
nex_date = date[:-2] + str(int(date[-2:]) + 1)
date_list = [
    pd.to_datetime(date + ' ' + x) if int(x[:2]) < 24 else pd.to_datetime(nex_date + ' ' + str(int(x[:2]) - 24) + x[2:])
    for x in stop_times.arrival_time]
stop_times.arrival_time = date_list

# Filter Stops file
stops = pd.read_csv(f'{path}/gtfs_o/stops.txt')
stops.stop_id = stops.stop_id.astype(str)
stops = pd.merge(stops, stops_map, on='stop_id').drop(columns=['location_type', 'stop_id', 'parent_station']).rename(
    columns={'new_stop_id': 'stop_id'})

# Rename Route_id starting from 1000
trip_groups = stop_times.groupby("trip_id")
stops_dict_rev = {}
route_map = {}
route_id = 1000     # Starting route id
temp_set = set()
for x, trip_detail in tqdm(trip_groups):
    route_seq = tuple(trip_detail.sort_values(by='stop_sequence')['stop_id'])
    if route_seq not in temp_set:
        stops_dict_rev[route_seq] = route_id
        temp_set.add((route_seq))
        route_id = route_id + 1
    route_map[x] = stops_dict_rev[route_seq]
print(route_id)

# Update new route_id in stoptimes file
route_map_db = pd.DataFrame(route_map.items(), columns=['trip_id', 'new_route_id'])
stop_times = pd.merge(stop_times, route_map_db, on='trip_id').drop(columns=['route_id']).rename(
    columns={'new_route_id': 'route_id'})
trips = pd.merge(trips, route_map_db, on='trip_id').drop(columns=['route_id']).rename(
    columns={'new_route_id': 'route_id'})

#########################################################################################################################
trip_map = {}
route_groups = stop_times.groupby("route_id")
if len(trips) != len(stop_times[stop_times.stop_sequence == 0]):
    print("Error: Not every trip has first stop, rewrite code below")
else:
    for rid, trip_detail in tqdm(route_groups):
        trip_seq = enumerate(
            list(trip_detail[trip_detail.stop_sequence == 0].sort_values(by='arrival_time')['trip_id']))
        for x in trip_seq:
            trip_map[x[1]] = f'{rid}_{x[0]}'

trip_map_db = pd.DataFrame(trip_map.items(), columns=['trip_id', 'new_trip_id'])
stop_times = pd.merge(stop_times, trip_map_db, on='trip_id').drop(columns=['trip_id']).rename(
    columns={'new_trip_id': 'trip_id'})
trips = pd.merge(trips, trip_map_db, on='trip_id').drop(columns=['trip_id']).rename(columns={'new_trip_id': 'trip_id'})
#########################################################################################################################
# Remove overlapping trips, i.e., Trips should follow FIFO rule
overlap = set()
route_groups = stop_times.groupby("route_id")
for r_idx, route_trips in tqdm(route_groups):
    route_trips_groups = route_trips.groupby('trip_id')
    route_trips_list = []
    for _, x in route_trips_groups:
        route_trips_list.append(tuple(x.arrival_time))
    route_trips_list.sort(key=lambda x: x[0])
    for x in range(len(route_trips_list) - 1):
        first_trip = route_trips_list[x]
        second_trip = route_trips_list[x + 1]
        if any([second_trip[idx[0]] <= first_trip[idx[0]] for idx in enumerate(first_trip)]):
            overlap = overlap.union({r_idx})
if overlap:
    print(f"{len(overlap)} have overlapping trips")
stop_times = stop_times[~stop_times.route_id.isin(overlap)]

#########################################################################################################################
# Remove trips with length <2.
trip_group = stop_times.groupby('trip_id')
for x, trip_details in tqdm(trip_group):
    if len(trip_group) < 2:
        print(x)
        print('remove these')
#########################################################################################################################
stops_group = stop_times[['stop_id', "route_id"]].groupby('stop_id')
routes_group = stop_times.groupby('route_id')
solo_routes = set()
for rid, route_details in routes_group:
    intersect = 0
    stops_seq = set(route_details.stop_id)
    for x in stops_seq:
        if len(set(stops_group.get_group(x)['route_id']).difference({rid})) > 0:
            intersect = 1
            break
    if intersect == 0:
        solo_routes.add(rid)
stop_times = stop_times[~stop_times.route_id.isin(solo_routes)].sort_values(
    by=['route_id', 'stop_sequence']).drop(columns=['route_id'])
#########################################################################################################################
# Drop routes circling back to same stop
stop_times = stop_times.drop_duplicates(subset=['trip_id', 'stop_id'])
#########################################################################################################################
# For every trip stop_sequence should be continuous sequence starting from 0.
stop_times['stop_sequence'] = stop_times.groupby("trip_id")["stop_sequence"].rank(method="first",
                                                                                  ascending=True).astype(int) - 1
#########################################################################################################################
# Rename all trip_id with following format: Routeid_trip_count.
# E.g., 502_4 is 4th trip (sorted according to departure time) on route 502.
trips = trips[trips.trip_id.isin(stop_times.trip_id)].drop(columns=['direction_id', 'service_id', 'trip_headsign', 'trip_short_name'])
stops = stops[stops.stop_id.isin(stop_times.stop_id)]
_, tid_list = zip(*trips.trip_id.str.split('_'))
trips['tid'] = tid_list
trips['tid'] = trips['tid'].astype(int)
trips['tid'] = trips.groupby("route_id")['tid'].rank(method="first", ascending=True).astype(int) - 1
trips['new_trip_id'] = trips['route_id'].astype(str) + "_" + trips['tid'].astype(str)
stop_times = pd.merge(stop_times, trips, on='trip_id').drop(columns=['trip_id', 'tid', 'route_id']).rename(
    columns={'new_trip_id': 'trip_id'})
trips = trips.drop(columns=['trip_id', 'tid']).rename(columns={'new_trip_id': 'trip_id'})

#########################################################################################################################
# Build transfers file
transfers = np.load(f'./GTFS/{path}/{path}_dist_mat.npy')
# transfers is numpy array of distance between stops. This can be obtained using OpenStreetMap.
if len(transfers) != len(stops):
    print(f'Error: Length mismatch for distance matrix & stops')
stops = stops.sort_values(by='stop_id').reset_index(drop=True)
walking_limit = 180  # Distance is in meter and assumed speed is 1m/s
(row, col), value = (np.where((transfers <= walking_limit) & (transfers > 0))), transfers[(transfers <= walking_limit) & (transfers > 0)]
transfers = pd.DataFrame(list(zip(stops.stop_id.loc[row], stops.stop_id.loc[col], value)),
                         columns=['from_stop_id', 'to_stop_id', 'min_transfer_time'])
transfers = transfers.drop_duplicates(subset=['from_stop_id', 'to_stop_id'])

G = nx.Graph()  # Ensure transitive closure of footpath graph
edges = list(zip(transfers.from_stop_id, transfers.to_stop_id, transfers.min_transfer_time))
G.add_weighted_edges_from(edges)
connected = [c for c in nx.connected_components(G)]
for tree in connected:
    for source in tree:
        for desti in tree:
            if source != desti and (source, desti) not in G.edges():
                G.add_edge(source, desti, weight=nx.dijkstra_path_length(G, source, desti))
footpath = list(G.edges(data=True))
reve_edges = [(x[1], x[0], x[-1]) for x in G.edges(data=True)]
footpath.extend(reve_edges)
transfers = pd.DataFrame(footpath)
transfers[2] = transfers[2].apply(lambda x: list(x.values())[0])
transfers.rename(columns={0: "from_stop_id", 1: "to_stop_id", 2: "min_transfer_time"}, inplace=True)
transfers.sort_values(by=['min_transfer_time', 'from_stop_id', 'to_stop_id']).reset_index(drop=True)
#########################################################################################################################
# Save the files to read location
transfers.to_csv(f'{path}/GTFS/stops.csv', index=False)
trips.to_csv(f'{path}/GTFS/trips.txt', index=False)
stop_times.to_csv(f'{path}/GTFS/stop_times.txt', index=False)
stop_times.to_csv(f'{path}/GTFS/stop_times.csv', index=False)
stops.to_csv(f'{path}/GTFS/stops.txt', index=False)
stops.to_csv(f'{path}/GTFS/stops.csv', index=False)
#########################################################################################################################
# Save the files to save location
transfers.to_csv(f'{save_path}/transfers.txt', index=False)
stop_times.to_csv(f'{save_path}/stop_times.csv', index=False)
stops.to_csv(f'{save_path}/stops.txt', index=False)
stops.to_csv(f'{save_path}/stops.csv', index=False)
trips.to_csv(f'{save_path}/trips.txt', index=False)
#########################################################################################################################
# Print final statistics
print(f'Final stops count    : {len(stops)}')
print(f'Final trips count    : {len(trips)}')
print(f'Final routes count   : {len(set(trips.route_id))}')
print(f'Final transfers count: {len(transfers)}')
