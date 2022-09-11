"""
Apply necessary filters to GTFS set. Note that this file is GTFS-specific.
"""
import pandas as pd
from tqdm import tqdm
import numpy as np
import networkx as nx


# Specify paths

def save_final(READ_PATH: str, SAVE_PATH: str, trips, stop_times, stops, *argv) -> None:
    """
    Save the final GTFS set and print statistics

    Args:
        READ_PATH (str): Path to read GTFS
        SAVE_PATH (str): Path to save GTFS
        trips: GTFS trips.txt file
        stop_times: GTFS stop_times.txt file
        stops: GTFS stops.txt file
        *argv: GTFS transfers.txt file

    Returns:
        None
    """
    for arg in argv:
        arg.to_csv(f'{READ_PATH}/GTFS/stops.csv', index=False)
    trips.to_csv(f'{READ_PATH}/GTFS/trips.txt', index=False)
    stop_times.to_csv(f'{READ_PATH}/GTFS/stop_times.txt', index=False)
    stop_times.to_csv(f'{READ_PATH}/GTFS/stop_times.csv', index=False)
    stops.to_csv(f'{READ_PATH}/GTFS/stops.txt', index=False)
    stops.to_csv(f'{READ_PATH}/GTFS/stops.csv', index=False)
    #####################################
    # Save the files to save location
    for arg in argv:
        arg.to_csv(f'{SAVE_PATH}/transfers.txt', index=False)
    stop_times.to_csv(f'{SAVE_PATH}/stop_times.csv', index=False)
    stops.to_csv(f'{SAVE_PATH}/stops.txt', index=False)
    stops.to_csv(f'{SAVE_PATH}/stops.csv', index=False)
    trips.to_csv(f'{SAVE_PATH}/trips.txt', index=False)
    #####################################
    # Print final statistics
    print(f'Final stops count    : {len(stops)}')
    print(f'Final trips count    : {len(trips)}')
    print(f'Final routes count   : {len(set(trips.route_id))}')
    for arg in argv:
        print(f'Final transfers count: {len(arg)}')


def remove_unwanted_route(unwanted_route: list, route) -> tuple:
    """
    Remove unwanted routes like sea ferries, Metro

    Args:
        unwanted_route (list):
        route: GTFS routes.txt file

    Returns:
        Filters route file and a set containing all routes ids.
    """
    print("removing unwanted routes")
    valid_route_types = list(set(route.route_type))
    print(f"Total routes: {len(route)}")
    print(f"Total route types: {route.route_type.value_counts()}")
    valid_route_types = [x for x in valid_route_types if x not in unwanted_route]
    route = route[route.route_type.isin(valid_route_types)]
    valid_routes_set = set(route.route_id)
    print(f"Valid route after filtering: {len(valid_routes_set)}")
    return valid_routes_set, route


def filter_trips_routes_ondates(valid_routes_set: set, calendar_dates, trips, date: int) -> tuple:
    """
    Filter the trips file based on calendar date. Only One-days data is assumed here

    Args:
        valid_routes_set (set): set containing valid route ids
        calendar_dates: GTFS Calendar_dates.txt file
        trips: GTFS trips.txt file
        date (int): date on which GTFS set is filtered

    Returns:
        Filtered trips file and a set of valid trips and routes.
    """
    print("filtering trips based on date")
    if type(calendar_dates)==int:
        valid_trips = set(trips.trip_id)
        valid_route = set(trips.route_id)
        return trips, valid_trips, valid_route
    else:
        calendar_dates.sort_values(by='date', inplace=True)
        calendar_dates[(calendar_dates.exception_type == 1)].groupby('date').count().sort_values('service_id')
        valid_service_id = set(
            calendar_dates[(calendar_dates.date == date) & (calendar_dates.exception_type == 1)]['service_id'])
        trips = trips[trips.service_id.isin(valid_service_id) & trips.route_id.isin(valid_routes_set)]
        valid_trips = set(trips.trip_id)
        valid_route = set(trips.route_id)
        print(f"After Filtering on date {date}")
        print(f"Valid trips:  {len(valid_trips)}")
        print(f"Valid routes:  {len(valid_route)}")
        return trips, valid_trips, valid_route


def filter_stoptimes(valid_trips: set, trips, date: int, stop_times) -> tuple:
    """
    Filter stoptimes file

    Args:
        valid_trips (set): GTFS set containing trips
        trips: GTFS trips.txt file
        date (int): date on which GTFS set is filtered
        stop_times: GTFS stoptimes.txt file

    Returns:
        Filtered stops mapping and stoptimes file
    """
    print("filtering stop_times.txt")
    stop_times.stop_sequence = stop_times.stop_sequence - 1
    stop_times.stop_id = stop_times.stop_id.astype(str)
    stop_times = stop_times[stop_times.trip_id.isin(valid_trips)]
    stop_times['stop_sequence'] = stop_times.groupby("trip_id")["stop_sequence"].rank(method="first",
                                                                                      ascending=True).astype(int) - 1
    stop_times = pd.merge(stop_times, trips, on='trip_id')
    stops_map = pd.DataFrame([t[::-1] for t in enumerate(set(stop_times.stop_id), 1)], columns=['stop_id', 'new_stop_id'])
    stop_times = pd.merge(stop_times, stops_map, on='stop_id').drop(columns=['stop_id']).rename(columns={'new_stop_id': 'stop_id'})
    date = f'{str(date)[:4]}-{str(date)[4:6]}-{str(date)[6:]}'
    nex_date = date[:-2] + str(int(date[-2:]) + 1)
    date_list = [
        pd.to_datetime(date + ' ' + x) if int(x[:2]) < 24 else pd.to_datetime(nex_date + ' ' + str(int(x[:2]) - 24) + x[2:])
        for x in stop_times.arrival_time]
    stop_times.arrival_time = date_list
    return stops_map, stop_times


def filter_stopsfile(stops_map, stops):
    """
        Apply filter to stops file

    Args:
        stops_map: stop id mapping
        stops: GTFS stops.txt file

    Returns:
        Filtered stops file
    """
    print("filtering stops.txt")
    stops.stop_id = stops.stop_id.astype(str)
    stops = pd.merge(stops, stops_map, on='stop_id').drop(columns=['stop_id']).rename(columns={'new_stop_id': 'stop_id'})
    print(f"Stops in stoptimes file = {len(stops)}")
    return stops


def rename_route(stop_times, trips) -> tuple:
    """
        Rename the route Id to integer. Route Id are assumed to start from 1000.

    Args:
        stop_times: GTFS stoptimes.txt file
        trips: GTFS trips.txt file

    Returns:
        Route Id mapping, filtered stoptimes and trip file
    """
    print("renaming routes")
    trip_groups = stop_times.groupby("trip_id")
    stops_dict_rev = {}
    route_map = {}
    route_id = 1000  # Rename Route_id starting from 1000
    temp_set = set()
    for x, trip_detail in tqdm(trip_groups):
        route_seq = tuple(trip_detail.sort_values(by='stop_sequence')['stop_id'])
        if route_seq not in temp_set:
            stops_dict_rev[route_seq] = route_id
            temp_set.add((route_seq))
            route_id = route_id + 1
        route_map[x] = stops_dict_rev[route_seq]
    # Update new route_id in stoptimes file
    route_map_db = pd.DataFrame(route_map.items(), columns=['trip_id', 'new_route_id'])
    stop_times = pd.merge(stop_times, route_map_db, on='trip_id').drop(columns=['route_id']).rename(
        columns={'new_route_id': 'route_id'})
    trips = pd.merge(trips, route_map_db, on='trip_id').drop(columns=['route_id']).rename(
        columns={'new_route_id': 'route_id'})
    return route_map_db, stop_times, trips


def remove_overlapping_trips(stop_times):
    """
    Remove overlapping trips, i.e., all trips should follow first-in-first-out (FIFO) property.

    Args:
        stop_times: GTFS stoptimes.txt file

    Returns:
        Filtered stoptimes file
    """
    print("checking overlapping trips")
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
        print(f"{len(overlap)} had overlapping trips")
    stop_times = stop_times[~stop_times.route_id.isin(overlap)]
    return stop_times


def build_transfers_file(READ_PATH: str, stops, walking_limit: int):
    """
    Build transfers file. This function requires distance matrix of stops. The matrix should be saved inside READ_PATH directory.
    Note that the generated transfers file is transitively closed.

    Args:
        READ_PATH (str): Path to read GTFS
        stops: GTFS stops.txt filr
        walking_limit (int): maximum allowed limit on walking

    Returns:
        GTFS transfer.txt file
    """
    print("building transfers file")
    # Build transfers file
    transfers = np.load(f'./GTFS/{READ_PATH}/{READ_PATH}_dist_mat.npy')
    # transfers is a numpy array of distance between stops. Its dimension should be stops x stops. This can be obtained using OpenStreetMap.
    if len(transfers) != len(stops):
        print(f'Error: Length mismatch for distance matrix & stops')
    stops = stops.sort_values(by='stop_id').reset_index(drop=True)
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
    return transfers


def filter_trips(trips, stop_times, stops):
    """
    Filter trips file. Trip Id are renamed as a_b where a is the route id and b is the sequence of
    trip (arranged according to departure time)

    Args:
        trips: GTFS trips.txt file
        stop_times: GTFS stoptimes.txt file
        stops: GTFS stops.txt file

    Returns:
        Filtered trips, stoptimes and stops file
    """
    print("applying final trips filter")
    # Rename all trip_id with following format: Routeid_trip_count.
    # E.g., 502_4 is 4th trip (sorted according to departure time) on route 502.
    trips = trips[trips.trip_id.isin(stop_times.trip_id)].drop(columns=['service_id'])
    stops = stops[stops.stop_id.isin(stop_times.stop_id)]
    _, tid_list = zip(*trips.trip_id.str.split('_'))
    trips['tid'] = tid_list
    trips['tid'] = trips['tid'].astype(int)
    trips['tid'] = trips.groupby("route_id")['tid'].rank(method="first", ascending=True).astype(int) - 1
    trips['new_trip_id'] = trips['route_id'].astype(str) + "_" + trips['tid'].astype(str)
    stop_times = pd.merge(stop_times, trips, on='trip_id').drop(columns=['trip_id', 'tid', 'route_id']).rename(
        columns={'new_trip_id': 'trip_id'})
    trips = trips.drop(columns=['trip_id', 'tid']).rename(columns={'new_trip_id': 'trip_id'})
    return trips, stop_times, stops


def stoptimes_filter(stop_times):
    """
    Apply filters to stoptimes file. Following filters are applied:
        1. Remove singleton routes, i.e., route of length 1. These can come due to various filters applied before.
        2. Drop routes circling back to same stop
        3. Rename stop_sequence for every trip starting from 0

    Args:
        stop_times: GTFS stoptimes.txt file

    Returns:
        Filtered stoptimes.txt GTFS file
    """
    print("applying final stoptimes filter")
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
    ##########################################
    # Drop routes circling back to same stop
    stop_times = stop_times.drop_duplicates(subset=['trip_id', 'stop_id'])
    ##########################################
    # For every trip stop_sequence should be continuous sequence starting from 0.
    stop_times['stop_sequence'] = stop_times.groupby("trip_id")["stop_sequence"].rank(method="first",
                                                                                      ascending=True).astype(int) - 1
    ##########################################

    return stop_times


def rename_trips(stop_times, trips):
    """
    Rename trips

    Args:
        stop_times: GTFS stoptimes.txt file
        trips: GTFS trips.txt file

    Returns:
        Filtered stoptimes.txt and trips.txt file
    """
    print("renaming trips")
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
    return stop_times, trips


def check_trip_len(stop_times) -> None:
    """
    Ensures that number of stops in all trips should be >2.

    Args:
        stop_times: GTFS stoptimes.txt file

    Returns:
        None
    """
    print("checking trips length")
    trip_group = stop_times.groupby('trip_id')
    for x, trip_details in tqdm(trip_group):
        if len(trip_group) < 2:
            print(x)
            print('Warning: Trips of len<2 present in stoptimes')
    return None


def read_gtfs(READ_PATH: str):
    """
    Reads the GTFS set

    Args:
        READ_PATH (str): Path to read GTFS

    Returns:
        GTFS files
    """
    print("reading GTFS data")
    stop_times_column = ['arrival_time', 'stop_sequence', 'stop_id', 'trip_id']
    stops_column = ['stop_lat', 'stop_lon', 'stop_id']
    trips_column = ['route_id', 'trip_id', 'service_id']
    calendar_dates = -1
    try:
        calendar_dates = pd.read_csv(f'{READ_PATH}/gtfs_o/calendar_dates.txt')
    except FileNotFoundError:
        print("calender_dates.txt missing")
    try:
        route = pd.read_csv(f'{READ_PATH}/gtfs_o/routes.txt')
    except FileNotFoundError:
        raise FileNotFoundError("routes.txt missing")
    try:
        trips = pd.read_csv(f'{READ_PATH}/gtfs_o/trips.txt', usecols=trips_column)
    except FileNotFoundError:
        raise FileNotFoundError("trips.txt missing")
    try:
        stop_times = pd.read_csv(f'{READ_PATH}/gtfs_o/stop_times.txt', usecols=stop_times_column)
    except FileNotFoundError:
        raise FileNotFoundError("stop_times.txt missing")
    try:
        stops = pd.read_csv(f'{READ_PATH}/gtfs_o/stops.txt', usecols=stops_column)
    except FileNotFoundError:
        raise FileNotFoundError("stops.txt missing")
    return calendar_dates, route , trips, stop_times, stops


def main(READ_PATH: str, SAVE_PATH: str, date: int, walking_limit: int, build_transfers: int) -> None:
    """
    Main function

    Args:
        READ_PATH (str): Path to read GTFS
        SAVE_PATH (str): Path to save GTFS
        date (int): date on which GTFS set is filtered
        walking_limit (int): maximum allowed limit on walking
        build_transfers (int): Parameter indicating whether to build transfers file or not

    Returns:
        None
    """
    calendar_dates, route,  trips, stop_times, stops = read_gtfs(READ_PATH)
    valid_routes, route = remove_unwanted_route(unwanted_route, route)
    trips, valid_trips, valid_route = filter_trips_routes_ondates(valid_routes, calendar_dates, trips, date)
    stops_map, stop_times = filter_stoptimes(valid_trips, trips, date, stop_times)
    stops = filter_stopsfile(stops_map, stops)
    route_map_db, stop_times, trips = rename_route(stop_times, trips)
    stop_times, trips = rename_trips(stop_times, trips)
    stop_times = remove_overlapping_trips(stop_times)
    check_trip_len(stop_times)
    stop_times = stoptimes_filter(stop_times)
    trips, stop_times, stops = filter_trips(trips, stop_times, stops)

    if build_transfers == 1:
        transfers = build_transfers_file(READ_PATH, stops, walking_limit)
        save_final(READ_PATH, SAVE_PATH, trips, stop_times, stops, transfers)
    else:
        save_final(READ_PATH, SAVE_PATH, trips, stop_times, stops)


if __name__ == "__main__":
    READ_PATH = './swiss'  # Path to unzipped GTFS set
    SAVE_PATH = f'./GTFS/{READ_PATH.split("/")[1]}'
    date = 20190610
    walking_limit = 180  # Distance is in meter and assumed speed is 1m/s
    unwanted_route = [2, 401, 1501, 1300, 900, 1000, 7, 1300]
    build_transfers = 1

    main(READ_PATH, SAVE_PATH, date, walking_limit, build_transfers)
