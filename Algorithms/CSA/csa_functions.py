import pickle
from collections import defaultdict

import pandas as pd


def initialize_csa(SOURCE: int, WALKING_FROM_SOURCE: int, footpath_dict: dict, D_TIME) -> tuple:
    """
    Initialize values for CSA.

    Args:
        SOURCE (int): stop id of source stop.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 indicates walking from SOURCE is allowed.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        D_TIME (pandas.datetime): departure time.

    Returns:
        stop_label(dict): dict to maintain best arrival label {stop id: pandas.datetime}.
        trip_set(dict): dict to check if a trip has been scanned or not{ trip id: boolean}.
        pi_label(dict): dict used for backtracking labels. Format {stop id : label}. label is ("walking", from stop, to_stop, footpath duration)
        or ('connection', connection id)
        inf_time (pandas.datetime): Variable indicating infinite time.

    """
    inf_time = pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")

    stop_label = defaultdict(lambda: inf_time)
    trip_set = defaultdict(lambda: False)
    pi_label = defaultdict(lambda: -1)

    stop_label[SOURCE] = D_TIME

    if WALKING_FROM_SOURCE == 1:
        try:
            for to_stop, duration in footpath_dict[SOURCE]:
                stop_label[to_stop] = D_TIME + duration
                pi_label[to_stop] = ("walking", SOURCE, to_stop, duration)
        except KeyError:
            pass

    return stop_label, trip_set, pi_label, inf_time


def load_connections_dict(NETWORK_NAME: str) -> list:
    """
    loads connection array.

    Args:
        NETWORK_NAME (str): Network name

    Returns:
        connections_list (list): list of connections. Format: [[connection id, fro stop, to stop, from time, to time, trip id]]

    """
    with open(f'./dict_builder/{NETWORK_NAME}/connections_dict_pkl.pkl', 'rb') as file:
        connections_list = pickle.load(file)
    return connections_list


def post_process_csa(SOURCE: int, DESTINATION: int, pi_label: dict, PRINT_ITINERARY: int, connections_list: list, stop_label: dict, inf_time) -> tuple:
    """
    Post processing functions for CSA. Currently supported functionality are
    1. Print complete journey

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        pi_label(dict): dict used for backtracking labels. Format {stop id : label}. label is ("walking", from stop, to_stop, footpath duration)
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        connections_list (list): list of connections. Format: [[connection id, fro stop, to stop, from time, to time, trip id]]
        stop_label(dict): dict to maintain best arrival label {stop id: pandas.datetime}.
        inf_time (pandas.datetime): Variable indicating infinite time.

    Returns:
        output (tuple): If the destination is not reachable (None), else tuple containing the best arrival time.

    """
    output = (None)
    if stop_label[DESTINATION]!=inf_time:
        output = (stop_label[DESTINATION])
    if PRINT_ITINERARY == 1:
        current_stop = DESTINATION
        if pi_label[current_stop] == -1:
            print('DESTINATION cannot be reached')
        else:
            journey = []
            while current_stop != SOURCE:
                current_label = pi_label[current_stop]
                # print(current_stop)
                if current_label[0] == 'connection':
                    connect = connections_list[current_label[1]]
                    # print(connect)
                    journey.append(connect[1:])
                    current_stop = connect[1]
                else:
                    footpath = current_label[1:]
                    # print(footpath)
                    journey.append(footpath)
                    current_stop = current_label[1]
            connection_journey = list(reversed(journey))
            _print_Journey_legs_csv(connection_journey)
    return output


def _print_Journey_legs_csv(journey: list)-> None:
    """
    prints the legs of journey for CSA
    #TODO: Combine legs by trips to get better output

    Args:
        journey (list): list of optimal labels

    Returns:
        None

    """
    for leg in journey:
        if len(leg) == 5:
            print(f"from {leg[0]} board at {leg[2].time()} and get down on {leg[1]} at {leg[3].time()} along {leg[4]}")
        else:
            print(f"from {leg[0]} walk till {leg[1]} for {leg[2].total_seconds()} seconds")
    return None
