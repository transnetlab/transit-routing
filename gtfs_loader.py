"""
Module contains functions to load the GTFS data.
"""


def load_all_dict(NETWORK_NAME: str):
    """
    Args:
        NETWORK_NAME (str): network NETWORK_NAME.

    Returns:
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): keys: route ID, values: list of trips in the increasing order of start time. Format-> dict[route_ID] = [trip_1, trip_2] where trip_1 = [(stop id, arrival time), (stop id, arrival time)]
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.
        routesindx_by_stop_dict (dict): Keys: stop id, value: [(route_id, stop index), (route_id, stop index)]

    Examples:
        >>> stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = load_all_dict('anaheim')

    """
    import pickle
    with open(f'./dict_builder/{NETWORK_NAME}/stops_dict_pkl.pkl', 'rb') as file:
        stops_dict = pickle.load(file)
    with open(f'./dict_builder/{NETWORK_NAME}/stoptimes_dict_pkl.pkl', 'rb') as file:
        stoptimes_dict = pickle.load(file)
    with open(f'./dict_builder/{NETWORK_NAME}/transfers_dict_full.pkl', 'rb') as file:
        footpath_dict = pickle.load(file)
    with open(f'./dict_builder/{NETWORK_NAME}/routes_by_stop.pkl', 'rb') as file:
        routes_by_stop_dict = pickle.load(file)
    with open(f'./dict_builder/{NETWORK_NAME}/idx_by_route_stop.pkl', 'rb') as file:
        idx_by_route_stop_dict = pickle.load(file)
    with open(f'./dict_builder/{NETWORK_NAME}/routesindx_by_stop.pkl', 'rb') as file:
        routesindx_by_stop_dict = pickle.load(file)
    return stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict


def load_all_db(NETWORK_NAME: str):
    """
    Args:
        NETWORK_NAME (str): name of the network

    Returns:
        stops_file (pandas.dataframe): dataframe with stop details.
        trips_file (pandas.dataframe): dataframe with trip details.
        stop_times_file (pandas.dataframe): dataframe with stoptimes details.
        transfers_file (pandas.dataframe): dataframe with transfers (footpath) details.

    Examples:
        >>> stops_file, trips_file, stop_times_file, transfers_file = load_all_db('anaheim')

    """
    import pandas as pd
    path = f"./Data/GTFS/{NETWORK_NAME}"
    stops_file = pd.read_csv(f'{path}/stops.txt', sep=',').sort_values(by=['stop_id']).reset_index(drop=True)
    trips_file = pd.read_csv(f'{path}/trips.txt', sep=',')
    stop_times_file = pd.read_csv(f'{path}/stop_times.txt', sep=',')
    stop_times_file.arrival_time = pd.to_datetime(stop_times_file.arrival_time)
    if "route_id" not in stop_times_file.columns:
        stop_times_file = pd.merge(stop_times_file, trips_file, on='trip_id')
    transfers_file = pd.read_csv(f'{path}/transfers.txt', sep=',')
    return stops_file, trips_file, stop_times_file, transfers_file
