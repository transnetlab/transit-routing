"""
Module defines a function to save (using pickling) the GTFS information in the form of a dictionary.
This is done for easy/faster data lookup.
"""

import pickle

import pandas as pd
from tqdm import tqdm


def build_save_route_by_stop(stop_times_file, NETWORK_NAME: str) -> dict:
    """
    This function saves a dictionary to provide easy access to all the routes passing through a stop_id.

    Args:
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        NETWORK_NAME (str): name of the network
    Returns:
        route_by_stop_dict_new (dict): keys: stop_id, values: list of routes passing through the stop_id. Format-> dict[stop_id] = [route_id]
    """
    print("building routes_by_stop")
    stops_by_route = stop_times_file.drop_duplicates(subset=['route_id', 'stop_sequence'])[
        ['stop_id', 'route_id']].groupby('stop_id')
    route_by_stop_dict = {id: list(routes.route_id) for id, routes in stops_by_route}

    with open(f'./dict_builder/{NETWORK_NAME}/routes_by_stop.pkl', 'wb') as pickle_file:
        pickle.dump(route_by_stop_dict, pickle_file)
    print("routes_by_stop done")
    return route_by_stop_dict


def build_save_stops_dict(stop_times_file, trips_file, NETWORK_NAME: str) -> dict:
    """
    This function saves a dictionary to provide easy access to all the stops in the route.

    Args:
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        trips_file (pandas.dataframe): trips.txt file in GTFS.
        NETWORK_NAME (str): name of the network
    Returns:
        stops_dict (dict): keys: route_id, values: list of stop id in the route_id. Format-> dict[route_id] = [stop_id]
    """
    print("building stops dict")
    import os
    path = f'./dict_builder/{NETWORK_NAME}/'
    if not os.path.exists(f'./dict_builder/{NETWORK_NAME}/'):
        os.makedirs(path)

    trips_group = stop_times_file.groupby("trip_id")  # This drops all trips for which timestamps are not sorted

    trips_with_correct_timestamps = [id for id, trip in tqdm(trips_group) if list(trip.arrival_time) == list(trip.arrival_time.sort_values())]
    if len(trips_with_correct_timestamps) != len(trips_file):
        print(f"Incorrect time sequence in stoptimes builder file")
    stop_times = stop_times_file[stop_times_file["trip_id"].isin(trips_with_correct_timestamps)]
    route_groups = stop_times.drop_duplicates(subset=['route_id', 'stop_sequence'])[['stop_id', 'route_id', 'stop_sequence']].groupby('route_id')
    stops_dict = {id: routes.sort_values(by='stop_sequence')['stop_id'].to_list() for id, routes in route_groups}

    with open(f'./dict_builder/{NETWORK_NAME}/stops_dict_pkl.pkl', 'wb') as pickle_file:
        pickle.dump(stops_dict, pickle_file)
    print("stops_dict done")
    return stops_dict


def build_save_stopstimes_dict(stop_times_file, trips_file, NETWORK_NAME: str) -> dict:
    """
    This function saves a dictionary to provide easy access to all the trips passing along a route id. Trips are sorted
    in the increasing order of departure time. A trip is list of tuple of form (stop id, arrival time)

    Args:
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        trips_file (pandas.dataframe): dataframe with transfers (footpath) details.
        NETWORK_NAME (str): name of the network
    Returns:
        stoptimes_dict (dict): keys: route ID, values: list of trips in the increasing order of start time. Format-> dict[route_ID] = [trip_1, trip_2] where trip_1 = [(stop id, arrival time), (stop id, arrival time)]
    """
    print("building stoptimes dict")

    stop_times_file.arrival_time = pd.to_datetime(stop_times_file.arrival_time)
    route_group = stop_times_file.groupby("route_id")
    stoptimes_dict = {r_id: [] for r_id, _ in route_group}
    for r_id, route in tqdm(route_group):
        trip_group = route.groupby("trip_id")  # Collect trip start points
        temp = route[route.stop_sequence == 0][["trip_id", "arrival_time"]].sort_values(by=["arrival_time"])
        for trip_id in temp["trip_id"]:  # Add them inorder
            trip = trip_group.get_group(trip_id).sort_values(by=["stop_sequence"])
            stoptimes_dict[r_id].append(list(zip(trip.stop_id, trip.arrival_time)))

    with open(f'./dict_builder/{NETWORK_NAME}/stoptimes_dict_pkl.pkl', 'wb') as pickle_file:
        pickle.dump(stoptimes_dict, pickle_file)
    print("stoptimes dict done")
    return stoptimes_dict


def build_save_footpath_dict(transfers_file, NETWORK_NAME: str) -> dict:
    """
    This function saves a dictionary to provide easy access to all the footpaths through a stop id.

    Args:
        transfers_file (pandas.dataframe): dataframe with transfers (footpath) details.
        NETWORK_NAME (str): name of the network
    Returns:
        footpath_dict (dict): keys: from stop_id, values: list of tuples of form (to stop id, footpath duration). Format-> dict[stop_id]=[(stop_id, footpath_duration)]
    """
    print("building footpath dict..")
    footpath_dict = {}
    g = transfers_file.groupby("from_stop_id")
    for from_stop, details in tqdm(g):
        footpath_dict[from_stop] = []
        for _, row in details.iterrows():
            footpath_dict[from_stop].append(
                (row.to_stop_id, pd.to_timedelta(float(row.min_transfer_time), unit='seconds')))

    with open(f'./dict_builder/{NETWORK_NAME}/transfers_dict_full.pkl', 'wb') as pickle_file:
        pickle.dump(footpath_dict, pickle_file)
    print("transfers_dict done")
    return footpath_dict


def build_stop_idx_in_route(stop_times_file, NETWORK_NAME: str) -> dict:
    """
    This function saves a dictionary to provide easy access to index of a stop in a route.

    Args:
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        NETWORK_NAME (str): name of the network
    Returns:
        idx_by_route_stop_dict (dict): Keys: (route id, stop id), value: stop index. Format {(route id, stop id): stop index in route}.
    """
    pandas_group = stop_times_file.groupby(["route_id", "stop_id"])
    idx_by_route_stop = {route_stop_pair: details.stop_sequence.iloc[0] for route_stop_pair, details in pandas_group}

    with open(f'./dict_builder/{NETWORK_NAME}/idx_by_route_stop.pkl', 'wb') as pickle_file:
        pickle.dump(idx_by_route_stop, pickle_file)
    print("idx_by_route_stop done")
    return idx_by_route_stop


def build_routesindx_by_stop_dict(NETWORK_NAME: str) -> dict:
    """
    This function saves a dictionary.

    Args:
        NETWORK_NAME (str): name of the network
    Returns:
        routesindx_by_stop_dict (dict): Keys: stop id, value: [(route_id, stop index), (route_id, stop index)]
    """
    with open(f'./dict_builder/{NETWORK_NAME}/stops_dict_pkl.pkl', 'rb') as file:
        stops_dict = pickle.load(file)
    with open(f'./dict_builder/{NETWORK_NAME}/routes_by_stop.pkl', 'rb') as file:
        routes_by_stop_dict = pickle.load(file)

    routesindx_by_stop_dict = {stop: list(zip(listofroutes, [stops_dict[x].index(stop) for x in listofroutes])) for stop, listofroutes in
                               routes_by_stop_dict.items()}

    with open(f'./dict_builder/{NETWORK_NAME}/routesindx_by_stop.pkl', 'wb') as pickle_file:
        pickle.dump(routesindx_by_stop_dict, pickle_file)
    print("routesindx_by_stop_dict done")
    return routesindx_by_stop_dict
