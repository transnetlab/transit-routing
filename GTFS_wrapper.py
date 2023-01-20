"""
Apply necessary filters to GTFS set. 
Note that this file is GTFS-specific.
"""
import pickle
import zipfile
from math import ceil

import pandas as pd
from tqdm import tqdm

pd.options.mode.chained_assignment = None  # default='warn'

def take_inputs() -> tuple:
    '''
    Takes the required inputs for building GTFS wrapper

    Returns:
        NETWORK_NAME, DATE_TOFILTER_ON, VALID_ROUTE_TYPES, BUILD_TRANSFER, breaker, READ_PATH, SAVE_PATH

    Examples:
        >>> NETWORK_NAME, DATE_TOFILTER_ON, VALID_ROUTE_TYPES, BUILD_TRANSFER, breaker, READ_PATH, SAVE_PATH = take_inputs()


    '''
    print("Rename the gtfs.zip to network_gtfs.zip and place it in main directory."
          " For example, for anaheim, place the anaheim_gtfs.zip in the main directory.")
    print("Enter Example parameters to build test case.")

    NETWORK_NAME = input("Enter Network name in small case. Example: anaheim\n: ")
    DATE_TOFILTER_ON = int(input("Enter date to filter on. Format: YYYYMMDD. Example: 20220630\n: "))
    # TODO: display options according to dataset
    VALID_ROUTE_TYPES = []
    while True:
        new_route_type = int(input("Enter route types to keep GTFS set. For example: 3 (bus routes). Press -1 when done\n: "))
        if new_route_type == -1:
            break
        else:
            VALID_ROUTE_TYPES.append(new_route_type)
    BUILD_TRANSFER = int(input("Enter 1 to build transfers file. Else press 0. Example: 0.\n: "))
    BUILD_TBTR_FILES = int(input("Enter 1 to build for TBTR preprocessing. Else press 0. Example: 1800\n: "))
    BUILD_TRANSFER_PATTERNS_FILES = int(input("Enter 1 to build Transfer Patterns preprocessing. Else press 0. Example: 0\n: "))
    BUILD_CSA = int(input("Enter 1 to build CSA preprocessing. Else press 0. Example: 0\n: "))

    print(f"Parameters entered: \n Network Name: {NETWORK_NAME}\n Date to filter on: {DATE_TOFILTER_ON}"
          f"\n Valid Route types: {VALID_ROUTE_TYPES}\n")
    if BUILD_TRANSFER == 1:
        print(" Build transfer file?: Yes")
    else:
        print(" Build transfer file?: No")

    if BUILD_TBTR_FILES == 1:
        print(" Build TBTR files?: Yes")
    else:
        print(" Build TBTR files?: No")

    if BUILD_TRANSFER_PATTERNS_FILES == 1:
        print(" Build Transfer Patterns files?: Yes")
    else:
        print(" Build Transfer Patterns files?: No")

    if BUILD_CSA == 1:
        print(" Build CSA files?: Yes")
    else:
        print(" Build CSA files?: No")

    print(breaker)
    # BUILD_TRANSFER = 0
    # WALKING_LIMIT = 180  # Distance is in meter and assumed speed is 1m/s
    # DATE_TOFILTER_ON = 20220815
    # NETWORK_NAME = './chicago'
    # VALID_ROUTE_TYPES = [3]
    READ_PATH = f'./Data/GTFS/{NETWORK_NAME}/gtfs_o'
    SAVE_PATH = f'./Data/GTFS/{NETWORK_NAME}/'
    param_list = [BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES, BUILD_TRANSFER_PATTERNS_FILES, BUILD_CSA]
    with open(f'./builders/parameters_entered.txt', 'wb') as pickle_file:
        pickle.dump(param_list, pickle_file)

    return NETWORK_NAME, DATE_TOFILTER_ON, VALID_ROUTE_TYPES, BUILD_TRANSFER, breaker, READ_PATH, SAVE_PATH


def read_gtfs(READ_PATH: str, NETWORK_NAME: str):
    """
    Reads the GTFS set

    Args:
        READ_PATH (str): Path to read GTFS
        NETWORK_NAME (str): Network name

    Returns:
        GTFS files


    Examples:
        >>> calendar_dates, route, trips, stop_times, stops, calendar, transfer = read_gtfs(READ_PATH, 'anaheim')

    """
    with zipfile.ZipFile(f'./{NETWORK_NAME}_gtfs.zip', 'r') as zip_ref:
        zip_ref.extractall(f'./Data/GTFS/{NETWORK_NAME}/gtfs_o')

    print("Reading GTFS data")
    print(f"Network: {NETWORK_NAME}")
    stop_times_column = ['arrival_time', 'stop_sequence', 'stop_id', 'trip_id']
    stops_column = ['stop_lat', 'stop_lon', 'stop_id']
    trips_column = ['route_id', 'trip_id', 'service_id']
    calendar_dates, calendar, transfer = None, None, None
    try:
        transfer = pd.read_csv(f'{READ_PATH}/transfer.txt')
    except FileNotFoundError:
        print("transfer.txt missing")
    try:
        calendar = pd.read_csv(f'{READ_PATH}/calendar.txt')
    except FileNotFoundError:
        print("calender.txt missing")
    try:
        calendar_dates = pd.read_csv(f'{READ_PATH}/calendar_dates.txt')
    except FileNotFoundError:
        print("calender_dates.txt missing")
    try:
        route = pd.read_csv(f'{READ_PATH}/routes.txt')
    except FileNotFoundError:
        raise FileNotFoundError("routes.txt missing")
    try:
        trips = pd.read_csv(f'{READ_PATH}/trips.txt', usecols=trips_column, low_memory=False)
    except FileNotFoundError:
        raise FileNotFoundError("trips.txt missing")
    try:
        stop_times = pd.read_csv(f'{READ_PATH}/stop_times.txt', usecols=stop_times_column, low_memory=False)
    except FileNotFoundError:
        raise FileNotFoundError("stop_times.txt missing")
    try:
        try:
            stops = pd.read_csv(f'{READ_PATH}/stops.txt', usecols=stops_column + ["stop_name"])
        except ValueError:
            stops = pd.read_csv(f'{READ_PATH}/stops.txt', usecols=stops_column)
    except FileNotFoundError:
        raise FileNotFoundError("stops.txt missing")
    print(breaker)
    return calendar_dates, route, trips, stop_times, stops, calendar, transfer


def remove_unwanted_route(VALID_ROUTE_TYPES: list, route) -> tuple:
    """
    Remove unwanted routes like sea ferries, Metro

    Args:
        VALID_ROUTE_TYPES (list):
        route: GTFS routes.txt file

    Returns:
        Filters route file and a set containing all routes ids.

    Examples:
        >>> valid_routes_set, route = remove_unwanted_route([3], route)

    """
    print("Removing unwanted routes")
    print(f"Total routes: {len(route)}")
    print(f"Route types distribution:\n {route.route_type.value_counts()}")
    route = route[route.route_type.isin(VALID_ROUTE_TYPES)]
    valid_routes_set = set(route.route_id)
    print(f"Total routes after filtering on route_types: {len(valid_routes_set)}")
    print(breaker)
    return valid_routes_set, route


def filter_trips_routes_ondates(valid_routes_set: set, calendar_dates, calendar, trips, DATE_TOFILTER_ON: int) -> tuple:
    """
    Filter the trips file based on calendar. Only One-days data is assumed here.

    Args:
        valid_routes_set (set): set containing valid route ids
        calendar_dates: GTFS Calendar_dates.txt file
        calendar: GTFS calendar.txt file
        trips: GTFS trips.txt file
        DATE_TOFILTER_ON (int): date on which GTFS set is filtered

    Returns:
        Filtered trips file and a set of valid trips and routes.

    Note:
        calendar_dates can be used in two sense. In the first case, it acts as a supplement to calendar.txt by defining listing the service id
        removed or added on a particular day (recommended usage).In the second case, it acts independently by listing all the service active
        on the particular day. See  GTFS reference for more details.
    """
    calendar.start_date, calendar.end_date = calendar.start_date.astype(int), calendar.end_date.astype(int)
    day_name = pd.to_datetime(DATE_TOFILTER_ON, format='%Y%m%d').day_name().lower()
    calendar = calendar[((calendar.start_date <= DATE_TOFILTER_ON) & (DATE_TOFILTER_ON <= calendar.end_date))]
    working_service_id = set(calendar[calendar[f'{day_name}'] == 1].service_id)
    new_service_id_added = set(calendar_dates[(calendar_dates.date == DATE_TOFILTER_ON) & (calendar_dates.exception_type == 1)].service_id)
    service_id_removed = set(calendar_dates[(calendar_dates.date == DATE_TOFILTER_ON) & (calendar_dates.exception_type == 2)].service_id)
    valid_service_id = working_service_id.union(new_service_id_added) - service_id_removed
    trips = trips[trips.service_id.isin(valid_service_id) & trips.route_id.isin(valid_routes_set)]
    valid_trips = set(trips.trip_id)
    valid_route = set(trips.route_id)
    print(f"After Filtering on date {DATE_TOFILTER_ON}")
    print(f"Valid trips:  {len(valid_trips)}")
    print(f"Valid routes:  {len(valid_route)}")
    return trips, valid_trips, valid_route

    # print(f"Filtering trips based on date: {DATE_TOFILTER_ON}")
    # if type(calendar_dates)==type(None):
    #     valid_trips = set(trips.trip_id)
    #     valid_route = set(trips.route_id)
    #     return trips, valid_trips, valid_route
    # else:
    #     calendar_dates.sort_values(by='date', inplace=True)
    #     calendar_dates[(calendar_dates.exception_type == 1)].groupby('date').count().sort_values('service_id')
    #     valid_service_id = set(
    #         calendar_dates[(calendar_dates.date == DATE_TOFILTER_ON) & (calendar_dates.exception_type == 1)]['service_id'])
    #     trips = trips[trips.service_id.isin(valid_service_id) & trips.route_id.isin(valid_routes_set)]
    #     valid_trips = set(trips.trip_id)
    #     valid_route = set(trips.route_id)
    #     print(f"Valid trips:  {len(valid_trips)}")
    #     print(f"Valid routes:  {len(valid_route)}")
    #     print(breaker)
    #     return trips, valid_trips, valid_route


def filter_stoptimes(valid_trips: set, trips, DATE_TOFILTER_ON: int, stop_times) -> tuple:
    """
    Filter stoptimes file

    Args:
        valid_trips (set): GTFS set containing trips
        trips: GTFS trips.txt file
        DATE_TOFILTER_ON (int): date on which GTFS set is filtered
        stop_times: GTFS stoptimes.txt file

    Returns:
        Filtered stops mapping and stoptimes file
    """
    print("Filtering stop_times.txt")
    stop_times.stop_sequence = stop_times.stop_sequence - 1
    stop_times.stop_id = stop_times.stop_id.astype(str)
    stop_times = stop_times[stop_times.trip_id.isin(valid_trips)]
    stop_times.loc[:, 'stop_sequence'] = stop_times.groupby("trip_id")["stop_sequence"].rank(method="first", ascending=True).astype(int) - 1

    stop_times = pd.merge(stop_times, trips, on='trip_id')
    stoplist = sorted(list(set(stop_times.stop_id)))
    stops_map = pd.DataFrame([t[::-1] for t in enumerate(stoplist, 1)], columns=['stop_id', 'new_stop_id'])
    stop_times = pd.merge(stop_times, stops_map, on='stop_id').drop(columns=['stop_id']).rename(columns={'new_stop_id': 'stop_id'})
    print("Applying dates")

    #Correct timestamp of format 9:30:00 to 09:30:00
    stop_times.arrival_time = [time_value if time_value.find(":")>1 else f"0{time_value}" for time_value in stop_times.arrival_time]

    DATE_TOFILTER_ON = f'{str(DATE_TOFILTER_ON)[:4]}-{str(DATE_TOFILTER_ON)[4:6]}-{str(DATE_TOFILTER_ON)[6:]}'
    last_stamp = stop_times.sort_values(by="arrival_time").arrival_time.iloc[-1]
    data_list = pd.date_range(DATE_TOFILTER_ON, periods=ceil(int(last_stamp[:2]) / 24))
    date_list = [data_list[int(int(x[:2]) / 24)] + pd.to_timedelta(str(int(x[:2]) - 24 * int(int(x[:2]) / 24)) + x[2:]) for x in tqdm(stop_times.arrival_time)]
    # nex_date = DATE_TOFILTER_ON[:-2] + str(int(DATE_TOFILTER_ON[-2:]) + 1)
    # date_list = [
    #     pd.to_datetime(DATE_TOFILTER_ON + ' ' + x) if int(x[:2]) < 24 else pd.to_datetime(nex_date + ' ' + str(int(x[:2]) - 24) + x[2:])
    #     for x in stop_times.arrival_time]
    stop_times.arrival_time = date_list
    print(breaker)
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
    print("Filtering stops.txt")
    stops.stop_id = stops.stop_id.astype(str)
    stops = pd.merge(stops, stops_map, on='stop_id').drop(columns=['stop_id']).rename(columns={'new_stop_id': 'stop_id'})
    print(f"Valid stops left: {len(stops)}")
    print(breaker)
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
    print("Renaming routes")
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
    print(breaker)
    return route_map_db, stop_times, trips


def rename_trips(stop_times, trips):
    """
    Rename trips

    Args:
        stop_times: GTFS stoptimes.txt file
        trips: GTFS trips.txt file

    Returns:
        Filtered stoptimes.txt and trips.txt file
    """
    print("Renaming trips")
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
    print(breaker)
    return stop_times, trips


def remove_overlapping_trips(stop_times, trips):
    """
    Remove overlapping trips, i.e., all trips should follow first-in-first-out (FIFO) property.

    Args:
        stop_times: GTFS stoptimes.txt file

    Returns:
        Filtered stoptimes file
    """
    print("Removing overlapping trips")
    # overlap = set()
    overlap_tid = []
    route_groups = stop_times.groupby("route_id")
    for r_idx, route_trips in tqdm(route_groups):
        route_trips_groups = route_trips.groupby('trip_id')
        route_trips_list = [(tid, tuple(trip.arrival_time)) for tid, trip in route_trips_groups]
        route_trips_list.sort(key=lambda x: x[1][0])
        for x in range(len(route_trips_list) - 1):
            f_tid, first_trip = route_trips_list[x]
            s_tid, second_trip = route_trips_list[x + 1]
            if any([second_trip[idx[0]] <= first_trip[idx[0]] for idx in enumerate(first_trip)]):
                # overlap = overlap.union({r_idx})
                overlap_tid.append(f_tid)
    if overlap_tid:
        print(f"{len(overlap_tid)} trips were overlapped")
    else:
        print(f"0 trips were overlapped")
    overlap_tid = set(overlap_tid)
    stop_times = stop_times[~stop_times.trip_id.isin(overlap_tid)]
    temp = set(stop_times.trip_id)
    trips = trips[trips.trip_id.isin(temp)]
    print(breaker)
    # if overlap:
    #     print(f"{len(overlap)} had overlapping trips")
    # stop_times = stop_times[~stop_times.route_id.isin(overlap)]
    return stop_times, trips


def check_trip_len(stop_times) -> None:
    """
    Ensures that number of stops in all trips should be >2.

    Args:
        stop_times: GTFS stoptimes.txt file

    Returns:
        None
    """
    print("Checking trips length")
    trip_group = stop_times.groupby('trip_id')
    for x, trip_details in tqdm(trip_group):
        if len(trip_group) < 2:
            print(x)
            print('Warning: Trips of len<2 present in stoptimes')
    print(breaker)
    return None


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
    print("Applying final stoptimes filter")
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
    print(breaker)
    return stop_times


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
    print("Applying final trips filter")
    # Rename all trip_id with following format: Routeid_trip_count.
    # E.g., 502_4 is 4th trip (sorted according to departure time) on route 502.
    # trips = trips[trips.trip_id.isin(stop_times.trip_id)].drop(columns=['service_id'])
    trips = trips[trips.trip_id.isin(stop_times.trip_id)]
    stops = stops[stops.stop_id.isin(stop_times.stop_id)].sort_values(by="stop_id").reset_index(drop=True)
    _, tid_list = zip(*trips.trip_id.str.split('_'))
    trips['tid'] = tid_list
    trips['tid'] = trips['tid'].astype(int)
    trips['tid'] = trips.groupby("route_id")['tid'].rank(method="first", ascending=True).astype(int) - 1
    trips['new_trip_id'] = trips['route_id'].astype(str) + "_" + trips['tid'].astype(str)
    stop_times = pd.merge(stop_times, trips, on='trip_id').drop(columns=['trip_id', 'tid', 'route_id']).rename(
        columns={'new_trip_id': 'trip_id'})
    trips = trips.drop(columns=['trip_id', 'tid']).rename(columns={'new_trip_id': 'trip_id'})
    print(breaker)
    return trips, stop_times, stops


def save_final(SAVE_PATH: str, trips, stop_times, stops) -> None:
    """
    Save the final GTFS set and print statistics

    Args:
        SAVE_PATH (str): Path to save GTFS
        trips: GTFS trips.txt file
        stop_times: GTFS stop_times.txt file
        stops: GTFS stops.txt file

    Returns:
        None
    """
    # Save the files to save location
    print("Saving files")
    stop_times.to_csv(f'{SAVE_PATH}/stop_times.csv', index=False)
    stop_times.to_csv(f'{SAVE_PATH}/stop_times.txt', index=False)
    stops.to_csv(f'{SAVE_PATH}/stops.txt', index=False)
    stops.to_csv(f'{SAVE_PATH}/stops.csv', index=False)
    trips.to_csv(f'{SAVE_PATH}/trips.txt', index=False)
    #####################################
    # Print final statistics
    print(f'Final stops count    : {len(stops)}')
    print(f'Final trips count    : {len(trips)}')
    print(f'Final routes count   : {len(set(trips.route_id))}')
    print(breaker)
    return None


def main() -> None:
    """
    Main function

    Returns:
        None
    #TODO: Call build_transfer_file if the parameter is 1
    """
    NETWORK_NAME, DATE_TOFILTER_ON, VALID_ROUTE_TYPES, BUILD_TRANSFER, breaker, READ_PATH, SAVE_PATH = take_inputs()
    calendar_dates, route, trips, stop_times, stops, calendar, transfer = read_gtfs(READ_PATH, NETWORK_NAME)
    valid_routes, route = remove_unwanted_route(VALID_ROUTE_TYPES, route)
    trips, valid_trips, valid_route = filter_trips_routes_ondates(valid_routes, calendar_dates, calendar, trips, DATE_TOFILTER_ON)
    stops_map, stop_times = filter_stoptimes(valid_trips, trips, DATE_TOFILTER_ON, stop_times)
    stops = filter_stopsfile(stops_map, stops)
    route_map_db, stop_times, trips = rename_route(stop_times, trips)
    stop_times, trips = rename_trips(stop_times, trips)
    stop_times, trips = remove_overlapping_trips(stop_times, trips)
    check_trip_len(stop_times)
    stop_times = stoptimes_filter(stop_times)
    trips, stop_times, stops = filter_trips(trips, stop_times, stops)
    save_final(SAVE_PATH, trips, stop_times, stops)
    return None
    # build_transfers_file(READ_PATH, stops, WALKING_LIMIT, transfer)


if __name__ == "__main__":
    breaker = "________________________________________________________________"
    main()
