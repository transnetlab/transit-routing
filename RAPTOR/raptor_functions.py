"""
Module contains function related to RAPTOR, rRAPTOR, One-To-Many rRAPTOR, HypRAPTOR
"""
from collections import deque as deque

import pandas as pd


def initialize_raptor(routes_by_stop_dict: dict, SOURCE: int, MAX_TRANSFER: int) -> tuple:
    '''
    Initialize values for RAPTOR.

    Args:
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        SOURCE (int): stop id of source stop.
        MAX_TRANSFER (int): maximum transfer limit.

    Returns:
        marked_stop (deque): deque to store marked stop.
        marked_stop_dict (dict): Binary variable indicating if a stop is marked. Keys: stop Id, value: 0 or 1.
        label (dict): nested dict to maintain label. Format {round : {stop_id: pandas.datetime}}.
        pi_label (dict): Nested dict used for backtracking labels. Format {round : {stop_id: pointer_label}}
        if stop is reached by walking, pointer_label= ('walking', from stop id, to stop id, time, arrival time)}} else pointer_label= (trip boarding time, boarding_point, stop id, arr_by_trip, trip id)
        star_label (dict): dict to maintain best arrival label {stop id: pandas.datetime}.
        inf_time (pd.timestamp): Variable indicating infinite time (pandas.datetime).

    Examples:
        >>> output = initialize_raptor(routes_by_stop_dict, 20775, 4)
    '''
    inf_time = pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")
#    inf_time = pd.to_datetime('2022-01-15 19:00:00')

    pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, MAX_TRANSFER + 1)}
    label = {x: {stop: inf_time for stop in routes_by_stop_dict.keys()} for x in range(0, MAX_TRANSFER + 1)}
    star_label = {stop: inf_time for stop in routes_by_stop_dict.keys()}

    marked_stop = deque()
    marked_stop_dict = {stop: 0 for stop in routes_by_stop_dict.keys()}
    marked_stop.append(SOURCE)
    marked_stop_dict[SOURCE] = 1
    return marked_stop, marked_stop_dict, label, pi_label, star_label, inf_time


def check_stop_validity(stops, SOURCE: int, DESTINATION: int) -> None:
    '''
    Check if the entered SOURCE and DESTINATION stop id are present in stop list or not.

    Args:
        stops: GTFS stops.txt
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.

    Returns:
        None

    Examples:
        >>> output = check_stop_validity(stops, 20775, 1482)
    '''
    if SOURCE in stops.stop_id and DESTINATION in stops.stop_id:
        print('correct inputs')
    else:
        print("incorrect inputs")
    return None

def get_latest_trip_new(stoptimes_dict: dict, route: int, arrival_time_at_pi, pi_index: int, change_time) -> tuple:
    '''
    Get latest trip after a certain timestamp from the given stop of a route.

    Args:
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        route (int): id of route.
        arrival_time_at_pi (pandas.datetime): arrival time at stop pi.
        pi_index (int): index of the stop from which route was boarded.
        change_time (pandas.datetime): change time at stop (set to 0).

    Returns:
        If a trip exists:
            trip index, trip
        else:
            -1,-1   (e.g. when there is no trip after the given timestamp)

    Examples:
        >>> output = get_latest_trip_new(stoptimes_dict, 1000, pd.to_datetime('2019-06-10 17:40:00'), 0, pd.to_timedelta(0, unit='seconds'))
    '''
    try:
        for trip_idx, trip in enumerate(stoptimes_dict[route]):
            if trip[pi_index][1] >= arrival_time_at_pi + change_time:
                return f'{route}_{trip_idx}', stoptimes_dict[route][trip_idx]
        return -1, -1  # No trip is found after arrival_time_at_pi
    except KeyError:
        return -1, -1  # No trip exsist for this route. in this case check tripid from trip file for this route and then look waybill.ID. Likely that trip is across days thats why it is rejected in stoptimes builder while checking


def post_processing(DESTINATION: int, pi_label: dict, PRINT_ITINERARY: int, label: dict) -> tuple:
    '''
    Post processing for std_RAPTOR. Currently supported functionality:
        1. Rounds in which DESTINATION is reached
        2. Trips for covering pareto optimal set
        3. Pareto optimal timestamps.

    Args:
        DESTINATION (int): stop id of destination stop.
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id. Format- {round : {stop_id: pointer_label}}
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        label (dict): nested dict to maintain label. Format {round : {stop_id: pandas.datetime}}.

    Returns:
        rounds_inwhich_desti_reached (list): list of rounds in which DESTINATION is reached. Format - [int]
        trip_set (list): list of trips ids required to cover optimal journeys. Format - [char]
        rap_out (list): list of pareto-optimal arrival timestamps. Format = [(pandas.datetime)]

    Examples:
        >>> output = post_processing(1482, pi_label, 1, label)
    '''
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]

    if rounds_inwhich_desti_reached == []:
        if PRINT_ITINERARY == 1:
            print('DESTINATION cannot be reached with given MAX_TRANSFERS')
        return None, None, None
    else:
        rounds_inwhich_desti_reached.reverse()
        pareto_set = []
        trip_set = []
        rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
        for k in rounds_inwhich_desti_reached:
            transfer_needed = k - 1
            journey = []
            stop = DESTINATION
            while pi_label[k][stop] != -1:
                journey.append(pi_label[k][stop])
                mode = pi_label[k][stop][0]
                if mode == 'walking':
                    stop = pi_label[k][stop][1]
                else:
                    trip_set.append(pi_label[k][stop][-1])
                    stop = pi_label[k][stop][1]
                    k = k - 1
            journey.reverse()
            pareto_set.append((transfer_needed, journey))

        if PRINT_ITINERARY == 1:
            _print_Journey_legs(pareto_set)
        #        _save_routesExplored(save_routes, routes_exp)
        return rounds_inwhich_desti_reached, trip_set, rap_out


def _print_Journey_legs(pareto_journeys: list) -> None:
    '''
    Prints journey in correct format. Parent Function: post_processing

    Args:
        pareto_journeys (list): pareto optimal set.

    Returns:
        None

    Examples:
        >>> output = _print_Journey_legs(pareto_journeys)
    '''
    for _, journey in pareto_journeys:
        for leg in journey:
            if leg[0] == 'walking':
                print(f'from {leg[1]} walk till  {leg[2]} for {leg[3].total_seconds()} seconds')
#                print(f'from {leg[1]} walk till  {leg[2]} for {leg[3]} minutes and reach at {leg[4].time()}')
            else:
                print(
                    f'from {leg[1]} board at {leg[0].time()} and get down on {leg[2]} at {leg[3].time()} along {leg[-1]}')
        print("####################################")
    return None

def post_processing_onetomany_rraptor(DESTINATION_LIST: list, pi_label: dict, PRINT_ITINERARY: int, label: dict, OPTIMIZED: int) -> list:
    '''
    post processing for Ont-To-Many rRAPTOR. Currently supported functionality:
        1. Print the output
        2. Routes required for covering pareto-optimal set.
        3. Trips required for covering pareto-optimal set.

    Args:
        DESTINATION_LIST (list): list of stop ids of destination stop.
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id. Format- {round : {stop_id: pointer_label}}
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        label (dict): nested dict to maintain label. Format {round : {stop_id: pandas.datetime}}.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.

    Returns:
        if OPTIMIZED==1:
            final_trips (list): list of trips required to cover all pareto-optimal journeys. format - [trip_id]
        elif OPTIMIZED==0:
            final_routes (list): list of routes required to cover all pareto-optimal journeys. format - [route_id]


    Examples:
        >>> output = post_processing_onetomany_rraptor([1482], pi_label, 1, label, 0)
    '''
    if OPTIMIZED == 1:
        final_trips = []
        for DESTINATION in DESTINATION_LIST:
            rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
            if rounds_inwhich_desti_reached:
                rounds_inwhich_desti_reached.reverse()
                trip_set = []
                for k in rounds_inwhich_desti_reached:
                    stop = DESTINATION
                    while pi_label[k][stop] != -1:
                        mode = pi_label[k][stop][0]
                        if mode == 'walking':
                            stop = pi_label[k][stop][1]
                        else:
                            trip_set.append(pi_label[k][stop][-1])
                            stop = pi_label[k][stop][1]
                            k = k - 1
                final_trips.extend(trip_set)
        return list(set(final_trips))
    else:
        final_routes = []
        for DESTINATION in DESTINATION_LIST:
            rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
            if rounds_inwhich_desti_reached == []:
                if PRINT_ITINERARY == 1:
                    print('DESTINATION cannot be reached with given MAX_TRANSFERS')
            else:
                rounds_inwhich_desti_reached.reverse()
                pareto_set = []
                trip_set = []
                # rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
                for k in rounds_inwhich_desti_reached:
                    transfer_needed = k - 1
                    journey = []
                    stop = DESTINATION
                    while pi_label[k][stop] != -1:
                        journey.append(pi_label[k][stop])
                        mode = pi_label[k][stop][0]
                        if mode == 'walking':
                            stop = pi_label[k][stop][1]
                        else:
                            trip_set.append(pi_label[k][stop][-1])
                            stop = pi_label[k][stop][1]
                            k = k - 1
                    journey.reverse()
                    pareto_set.append((transfer_needed, journey))
                    for trip in trip_set:
                        final_routes.append(int(trip.split("_")[0]))
                if PRINT_ITINERARY == 1:
                    _print_Journey_legs(pareto_set)
        return list(set(final_routes))


def post_processing_rraptor(DESTINATION: int, pi_label: dict, PRINT_ITINERARY: int, label: dict, OPTIMIZED: int) -> list:
    '''
    Full post processing for rRAPTOR. Currently supported functionality:
        1. Print the output
        2. Routes required for covering pareto-optimal journeys.
        3. Trips required for covering pareto-optimal journeys.

    Args:
        DESTINATION (int): stop id of destination stop.
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id. Format- {round : {stop_id: pointer_label}}
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        label (dict): nested dict to maintain label. Format {round : {stop_id: pandas.datetime}}.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.

    Returns:
        if OPTIMIZED==1:
            final_trips (list): List of trips required to cover all pareto-optimal journeys. Format - [trip_id]
        elif OPTIMIZED==0:
            final_routes (list): List of routes required to cover all pareto-optimal journeys. Format - [route_id]

    Examples:
        >>> output = post_processing_onetomany_rraptor([1482], pi_label, 1, label, 0)
    '''
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
    if OPTIMIZED == 1:
        final_trip = []
        if rounds_inwhich_desti_reached:
            rounds_inwhich_desti_reached.reverse()
            for k in rounds_inwhich_desti_reached:
                stop = DESTINATION
                while pi_label[k][stop] != -1:
                    mode = pi_label[k][stop][0]
                    if mode == 'walking':
                        stop = pi_label[k][stop][1]
                    else:
                        final_trip.append(pi_label[k][stop][-1])
                        stop = pi_label[k][stop][1]
                        k = k - 1
        return list(set(final_trip))
    else:
        final_routes = []
        if rounds_inwhich_desti_reached == []:
            if PRINT_ITINERARY == 1:
                print('DESTINATION cannot be reached with given MAX_TRANSFERS')
            return final_routes
        else:
            rounds_inwhich_desti_reached.reverse()
            pareto_set = []
            trip_set = []
            #rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
            for k in rounds_inwhich_desti_reached:
                transfer_needed = k - 1
                journey = []
                stop = DESTINATION
                while pi_label[k][stop] != -1:
                    journey.append(pi_label[k][stop])
                    mode = pi_label[k][stop][0]
                    if mode == 'walking':
                        stop = pi_label[k][stop][1]
                    else:
                        trip_set.append(pi_label[k][stop][-1])
                        stop = pi_label[k][stop][1]
                        k = k - 1
                journey.reverse()
                pareto_set.append((transfer_needed, journey))
                for trip in trip_set:
                    final_routes.append(int(trip.split("_")[0]))
            if PRINT_ITINERARY == 1:
                _print_Journey_legs(pareto_set)
        return final_routes