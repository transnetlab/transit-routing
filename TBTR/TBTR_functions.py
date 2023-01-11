"""
Module contains function related to TBTR, rTBTR, One-To-Many rTBTR, HypTBTR
"""
from collections import defaultdict

import pandas as pd


def initialize_tbtr(MAX_TRANSFER: int) -> dict:
    '''
    Initialize values for TBTR.

    Returns:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time. 
        inf_time (pandas.datetime): Variable indicating infinite time.

    Examples:
        >>> output = initialize_tbtr(4)
        >>> print(output)
    '''
    inf_time = pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")
    #    inf_time = pd.to_datetime("2023-01-26 20:00:00")
    J = {x: [inf_time, 0] for x in range(MAX_TRANSFER + 1)}
    return J


def initialize_onemany(MAX_TRANSFER: int, DESTINATION_LIST: list) -> tuple:
    '''
    Initialize values for one-to-many TBTR.

    Args:
        MAX_TRANSFER (int): maximum transfer limit.
        DESTINATION_LIST (list): list of stop ids of destination stop.

    Returns:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time.
        inf_time (pandas.datetime): Variable indicating infinite time.

    Examples:
        >>> output = initialize_onemany(4, [1482])
        >>> print(output)
    '''
    inf_time = pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")
    #    inf_time = pd.to_datetime("2023-01-26 20:00:00")
    J = {desti: {x: [inf_time, 0] for x in range(MAX_TRANSFER + 1)} for desti in DESTINATION_LIST}
    return J, inf_time


def initialize_from_desti(routes_by_stop_dict: dict, stops_dict: dict, DESTINATION: int, footpath_dict: dict, idx_by_route_stop_dict: dict) -> dict:
    '''
    Initialize routes/footpath to leading to destination stop.

    Args:
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        DESTINATION (int): stop id of destination stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.

    Returns:
        L (dict): A dict to track routes/leading to destination stop. Format {route_id: (from_stop_idx, travel time, stop id)}

    Examples:
        >>> output = initialize_from_desti(routes_by_stop_dict, stops_dict, 1482, footpath_dict, idx_by_route_stop_dict)
        >>> print(output)
    '''
    L_dict = defaultdict(lambda: [])
    try:
        transfer_to_desti = footpath_dict[DESTINATION]
        for from_stop, foot_time in transfer_to_desti:
            try:
                walkalble_desti_route = routes_by_stop_dict[from_stop]
                for route in walkalble_desti_route:
                    L_dict[route].append((idx_by_route_stop_dict[(route, from_stop)], foot_time, from_stop))
            except KeyError:
                pass
    except KeyError:
        pass
    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[DESTINATION]:
        L_dict[route].append((idx_by_route_stop_dict[(route, DESTINATION)], delta_tau, DESTINATION))
    return dict(L_dict)


def initialize_from_desti_onemany(routes_by_stop_dict: dict, stops_dict: dict, DESTINATION_LIST: list, footpath_dict: dict,
                                  idx_by_route_stop_dict: dict) -> dict:
    '''
    Initialize routes/footpath to leading to destination stop in case of one-to-many rTBTR

    Args:
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        DESTINATION_LIST (list): list of stop ids of destination stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.

    Returns:
        L (nested dict): A dict to track routes/leading to destination stops. Key: route_id, value: {destination_stop_id: [(from_stop_idx, travel time, stop id)]}

    Examples:
        >>> output = initialize_from_desti_onemany(routes_by_stop_dict, stops_dict, [1482], footpath_dict, idx_by_route_stop_dict)
        >>> print(output)
    '''
    L_dict_final = {}
    for destination in DESTINATION_LIST:
        L_dict = defaultdict(lambda: [])
        try:
            transfer_to_desti = footpath_dict[destination]
            for from_stop, foot_time in transfer_to_desti:
                try:
                    walkalble_desti_route = routes_by_stop_dict[from_stop]
                    for route in walkalble_desti_route:
                        L_dict[route].append((idx_by_route_stop_dict[(route, from_stop)], foot_time, from_stop))
                except KeyError:
                    pass
        except KeyError:
            pass
        delta_tau = pd.to_timedelta(0, unit="seconds")
        for route in routes_by_stop_dict[destination]:
            L_dict[route].append((idx_by_route_stop_dict[(route, destination)], delta_tau, destination))
        L_dict_final[destination] = dict(L_dict)
    return L_dict_final


def initialize_from_source(footpath_dict: dict, SOURCE: int, routes_by_stop_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                           D_TIME, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int, idx_by_route_stop_dict: dict) -> tuple:
    '''
    Initialize trips segments from source stop.

    Args:
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        SOURCE (int): stop id of source stop.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        D_TIME (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.

    Returns:
        R_t (dict): dict to store first reached stop of every trip. Format {trip_id: first reached stop}
        Q (list): list of trips segments

    Examples:
        >>> output = initialize_from_source(footpath_dict, 20775, routes_by_stop_dict, stops_dict, stoptimes_dict, pd.to_datetime('2019-06-10 00:00:00'), 4, 1, idx_by_route_stop_dict)
        >>> print(output)
    '''
    Q = [[] for x in range(MAX_TRANSFER + 2)]
    #    R_t = {f"{r}_{tid}": 1000 for r, r_trips in stoptimes_dict.items() for tid in range(len(r_trips))}
    R_t = defaultdict(lambda: 1000)  # assuming maximum route length is 1000
    connection_list = []
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                footpath_time = connection[1]
                walkable_source_routes = routes_by_stop_dict[connection[0]]
                for route in walkable_source_routes:
                    stop_index = idx_by_route_stop_dict[(route, connection[0])]
                    route_trip = stoptimes_dict[route]
                    for trip_idx, trip in enumerate(route_trip):
                        if D_TIME + footpath_time <= trip[stop_index][1]:
                            connection_list.append((f'{route}_{trip_idx}', stop_index))
                            break
        except KeyError:
            pass
    #    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[SOURCE]:
        stop_index = idx_by_route_stop_dict[(route, SOURCE)]
        route_trip = stoptimes_dict[route]
        for trip_idx, trip in enumerate(route_trip):
            if D_TIME <= trip[stop_index][1]:
                connection_list.append((f'{route}_{trip_idx}', stop_index))
                break
    enqueue(connection_list, 1, (0, 0), R_t, Q, stoptimes_dict)
    return R_t, Q


def enqueue(connection_list: list, nextround: int, predecessor_label: tuple, R_t: dict, Q: list, stoptimes_dict: dict) -> None:
    '''
    Main enqueue function used in TBTR to add trips segments to next round and update first reached stop of each trip.

    Args:
        connection_list (list): list of connections to be added. Format: [(to_trip_id, to_trip_id_stop_index)].
        nextround (int): next round/transfer number to which trip-segments are added.
        predecessor_label (tuple): used for backtracking journey ( To be developed ).
        R_t (dict): dict with keys as trip id. Format {trip_id : first reached stop}.
        Q (list): list of trips segments.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.

    Returns:
        None
    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[nextround].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, predecessor_label))
            for x in range(tid, len(stoptimes_dict[route])):
                new_tid = f"{route}_{x}"
                # R_t[new_tid] = min(R_t[new_tid], to_trip_id_stop)
                if R_t[new_tid] > to_trip_id_stop:
                    R_t[new_tid] = to_trip_id_stop


def update_label(label, no_of_transfer: int, predecessor_label: tuple, J: dict, MAX_TRANSFER: int) -> dict:
    '''
    Updates and returns destination pareto set.

    Args:
        label (pandas.datetime): optimal arrival time .
        no_of_transfer (int): number of transfer.
        predecessor_label (tuple): predecessor_label for backtracking (To be developed)
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        MAX_TRANSFER (int): maximum transfer limit.

    Returns:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
    '''
    J[no_of_transfer][1] = predecessor_label
    for x in range(no_of_transfer, MAX_TRANSFER + 1):
        if J[x][0] > label:
            J[x][0] = label
    return J


def post_process_range(J: dict, Q: list, rounds_desti_reached: list, PRINT_ITINERARY: int, DESTINATION: int, SOURCE: int,
                       footpath_dict: dict, stops_dict: dict, stoptimes_dict: dict, d_time, MAX_TRANSFER: int, trip_transfer_dict: dict) -> set:
    '''
    Contains all the post-processing features for rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal journeys.

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        rounds_desti_reached (list): Rounds in which DESTINATION is reached.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        DESTINATION (int): stop id of destination stop.
        SOURCE (int): stop id of source stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        D_TIME (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples

    Returns:
        necessory_trips (set): trips needed to cover pareto-optimal journeys.
    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    if PRINT_ITINERARY == 1:
        _print_tbtr_journey(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, d_time, MAX_TRANSFER, trip_transfer_dict,
                            rounds_desti_reached)
    necessory_trips = []
    for transfer_needed in reversed(rounds_desti_reached):
        no_of_transfer = transfer_needed
        current_trip = J[transfer_needed][1][0]
        journey = []
        while current_trip != 0:
            journey.append(current_trip)
            current_trip = [x for x in Q[no_of_transfer] if x[1] == current_trip][-1][-1][0]
            no_of_transfer = no_of_transfer - 1
        necessory_trips.extend(journey)
    return set(necessory_trips)


def initialize_from_source_range(dep_details: list, MAX_TRANSFER: int, stoptimes_dict: dict, R_t: dict) -> list:
    '''
    Initialize trips segments from source in rTBTR

    Args:
        dep_details (list): list of format [trip id, departure time, source index]
        MAX_TRANSFER (int): maximum transfer limit.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        R_t (nested dict): Nested_Dict with primary keys as trip id and secondary keys as number of transfers. Format {trip_id: {[round]: first reached stop}}

    Returns:
        Q (list): list of trips segments
    '''
    Q = [[] for x in range(MAX_TRANSFER + 2)]
    route, trip_idx = [int(x) for x in dep_details[0].split("_")]
    stop_index = dep_details[2]
    # _enqueue_range1(f'{route}_{trip_idx}', stop_index, n, (0, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
    connection_list = [(f'{route}_{trip_idx}', stop_index)]
    enqueue_range(connection_list, 1, (0, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
    return Q


def enqueue_range(connection_list: list, nextround: int, predecessor_label: tuple, R_t: dict, Q: list,
                  stoptimes_dict: dict, MAX_TRANSFER: int) -> None:
    '''
    Adds trips-segments to next round and update R_t. Used in range queries

    Args:
        connection_list (list): list of connections to be added. Format: [(to_trip_id, to_trip_id_stop_index)].
        nextround (int): next round/transfer number to which trip-segments are added
        predecessor_label (tuple): predecessor_label for backtracking journey ( To be developed ).
        R_t (nested dict): Nested_Dict with primary keys as trip id and secondary keys as number of transfers. Format {trip_id: {[round]: first reached stop}}
        Q (list): list of trips segments
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        MAX_TRANSFER (int): maximum transfer limit.

    Returns: None
    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[nextround][to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[nextround].append((to_trip_id_stop, to_trip_id, R_t[nextround][to_trip_id], route, tid, predecessor_label))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                for r in range(nextround, MAX_TRANSFER + 1):
                    new_tid = f"{route}_{x}"
                    if R_t[r][new_tid] > to_trip_id_stop:
                        R_t[r][new_tid] = to_trip_id_stop


def post_process_range_onemany(J: dict, Q: list, rounds_desti_reached: list, PRINT_ITINERARY: int, desti: int,
                               SOURCE: int, footpath_dict: dict, stops_dict: dict, stoptimes_dict: dict, d_time,
                               MAX_TRANSFER: int, trip_transfer_dict: dict) -> set:
    '''
    Contains all the post-processing features for One-To-Many rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal journeys.

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        rounds_desti_reached (list): Rounds in which DESTINATION is reached.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        desti (int): stop id of destination stop.
        SOURCE (int): stop id of source stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        d_time (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples

    Returns:
        TBTR_out (set): Trips needed to cover pareto-optimal journeys.

    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    if PRINT_ITINERARY == 1:
        _print_tbtr_journey_otm(J, Q, desti, SOURCE, footpath_dict, stops_dict, stoptimes_dict, d_time, MAX_TRANSFER, trip_transfer_dict, rounds_desti_reached)
    TBTR_out = []
    for transfer_needed in reversed(rounds_desti_reached):
        no_of_transfer = transfer_needed
        current_trip = J[desti][transfer_needed][1][0]
        journey = []
        while current_trip != 0:
            journey.append(current_trip)
            current_trip = [x for x in Q[no_of_transfer] if x[1] == current_trip][-1][-1][0]
            no_of_transfer = no_of_transfer - 1
        TBTR_out.extend(journey)
    return set(TBTR_out)


def post_process(J: dict, Q: list, DESTINATION: int, SOURCE: int, footpath_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                 PRINT_ITINERARY: int, D_TIME, MAX_TRANSFER: int, trip_transfer_dict: dict) -> list:
    '''
    Contains post-processing features for TBTR.
    Currently supported functionality:
        Collect pareto-optimal arrival timestamps.

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        DESTINATION (int): stop id of destination stop.
        SOURCE (int): stop id of source stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        D_TIME (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples

    Returns:
        TBTR_out (list): pareto-optimal arrival timestamps.
    '''
    rounds_desti_reached = [roundno for roundno in range(1, MAX_TRANSFER + 1) if J[roundno][1] != 0]
    if rounds_desti_reached == []:
        if PRINT_ITINERARY == 1:
            print('DESTINATION cannot be reached with given MAX_TRANSFERS')
    #        return -1
    else:
        if PRINT_ITINERARY == 1:
            _print_tbtr_journey(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, D_TIME, MAX_TRANSFER, trip_transfer_dict,
                                rounds_desti_reached)
        TBTR_out = []
        for x in reversed(rounds_desti_reached):
            TBTR_out.append(J[x][0])
        return TBTR_out


def _print_tbtr_journey(J: dict, Q: list, DESTINATION: int, SOURCE: int, footpath_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                        D_TIME, MAX_TRANSFER: int, trip_transfer_dict: dict, rounds_desti_reached: list) -> None:
    """
    Prints the output of TBTR

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        DESTINATION (int): stop id of destination stop.
        SOURCE (int): stop id of source stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        D_TIME (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples
        rounds_desti_reached (list): Rounds in which DESTINATION is reached.

    Returns:
        None

    Examples:
        >>> _print_tbtr_journey(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, D_TIME, MAX_TRANSFER, trip_transfer_dict, rounds_desti_reached)

    TODO:
        Build a better backtracking system for TBTR
    """
    for x in reversed(rounds_desti_reached):
        round_no = x
        journey = []
        trip_segement_counter = J[x][1][2]
        while round_no > 0:
            pred = Q[round_no][trip_segement_counter]
            journey.append((pred[5][0], pred[1], pred[0]))
            trip_segement_counter = pred[5][1]
            round_no = round_no - 1
        from_stop_list = []
        for id, t_transfer in enumerate(journey[:-1]):
            from_Stop_onwards = journey[id + 1][2]
            for from_stop, trasnsfer_list in trip_transfer_dict[t_transfer[0]].items():
                if from_stop < from_Stop_onwards:
                    continue
                else:
                    if (t_transfer[1], t_transfer[2]) in trasnsfer_list:
                        from_stop_list.append(from_stop)
        journey_final = [(journey[counter][0], x, journey[counter][1], journey[counter][2]) for counter, x in enumerate(from_stop_list)]
        # from source
        from_trip, from_stop_idxx = journey[-1][1], journey[-1][2]
        fromstopid = stops_dict[int(from_trip.split("_")[0])][from_stop_idxx]
        if fromstopid == SOURCE:
            journey_final.append(("trip", 0, from_trip, from_stop_idxx))
        else:
            for to_stop, to_time in footpath_dict[fromstopid]:
                if to_stop == SOURCE:
                    journey_final.append(("walk", SOURCE, fromstopid, to_time + D_TIME))
                    break
        # Add final lag. Destination can either be along the route or at a walking distance from it.
        if J[x][1][1] != (0, 0):  # Add here if the destination is at walking distance from final route
            try:
                final_route, boarded_from = int(journey_final[0][2].split("_")[0]), journey_final[0][3]
                found = 0
                for walking_from_stop_idx, stop_id in enumerate(stops_dict[final_route]):
                    if walking_from_stop_idx < boarded_from: continue
                    try:
                        for to_stop, to_stop_time in footpath_dict[stop_id]:
                            if to_stop == DESTINATION:
                                found = 1
                                journey_final.insert(0, ("walk", journey_final[0][2], boarded_from, walking_from_stop_idx,
                                                         to_stop_time))  # walking_pointer, from_trip, from_stop, to_stop
                                break
                    except KeyError:
                        continue
                    if found == 1: break
            except AttributeError:
                if len(journey_final) == 1:
                    final_route = int(J[x][1][0].split("_")[0])
                    boarded_from = stops_dict[final_route].index(journey_final[0][2])
                    found = 0
                    for walking_from_stop_idx, stop_id in enumerate(stops_dict[final_route]):
                        if walking_from_stop_idx < boarded_from: continue
                        try:
                            for to_stop, to_stop_time in footpath_dict[stop_id]:
                                if to_stop == DESTINATION:
                                    found = 1
                                    journey_final.insert(0, (
                                    "walk", J[x][1][0], boarded_from, walking_from_stop_idx, to_stop_time))  # walking_pointer, from_trip, from_stop, to_stop
                                    break
                        except KeyError:
                            continue
                        if found == 1: break
                else:
                    raise NameError
        else:  # Destination is along the route.
            try:
                final_route, boarded_from = int(journey_final[0][2].split("_")[0]), journey_final[0][3]
                desti_index = stops_dict[final_route].index(DESTINATION)
                journey_final.insert(0, ("trip", journey_final[0][2], boarded_from, desti_index))  # walking_pointer, from_trip, from_stop, to_stop
            except AttributeError:
                if len(journey_final) == 1:
                    final_route = int(J[x][1][0].split("_")[0])
                    boarded_from = stops_dict[final_route].index(journey_final[0][2])
                    desti_index = stops_dict[final_route].index(DESTINATION)
                    journey_final.insert(0, ("trip", J[x][1][0], boarded_from, desti_index))  # walking_pointer, from_trip, from_stop, to_stop
        if journey_final == []:
            tid = [int(x) for x in journey[0][1].split("_")]
            tostop_det = stops_dict[tid[0]].index(DESTINATION)
            journey_final.append((journey[0][1], stoptimes_dict[tid[0]][tid[1]][journey[0][2]], stoptimes_dict[tid[0]][tid[1]][tostop_det]))
        journey_final.reverse()
        journey_final_copy = journey_final.copy()
        journey_final.clear()
        for c, leg in enumerate(journey_final_copy):
            if c == 0:
                if leg[0] == "trip":
                    [trip_route, numb], fromstopidx = [int(x) for x in leg[2].split("_")], leg[3]
                    try:
                        journey_final.append(
                            [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][1]]])
                    except TypeError:
                        try:
                            journey_final.append([leg[2], stoptimes_dict[trip_route][numb][fromstopidx],
                                                  stoptimes_dict[trip_route][numb][stops_dict[trip_route].index(DESTINATION)]])
                            break
                        except ValueError:
                            journey_final.append(
                                [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][3]]])
                elif leg[0] == "walk":
                    journey_final.append(("walk", leg[1], leg[2], [time for stop, time in footpath_dict[leg[1]] if stop == leg[2]][0]))
            elif c == len(journey_final_copy) - 1:
                if leg[0] == "trip":
                    [trip_route, numb], fromstopidx, tostopidx = [int(x) for x in leg[1].split("_")], leg[2], leg[3]
                    journey_final.append([leg[1], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]])
                elif leg[0] == "walk":
                    from_trip = [int(x) for x in leg[1].split("_")]
                    journey_final.append((leg[1], stoptimes_dict[from_trip[0]][from_trip[1]][leg[2]], stoptimes_dict[from_trip[0]][from_trip[1]][leg[3]]))
                    foot_connect = stoptimes_dict[from_trip[0]][from_trip[1]][leg[3]]
                    last_foot_tme = [time for stop, time in footpath_dict[foot_connect[0]] if stop == DESTINATION][0]
                    journey_final.append(
                        ("walk", foot_connect[0], DESTINATION, last_foot_tme, stoptimes_dict[from_trip[0]][from_trip[1]][leg[3]][1] + last_foot_tme))
            else:
                if c == 1:
                    if journey_final_copy[c - 1][0] == "walk":
                        [trip_route, numb], tostopidx = [int(x) for x in leg[0].split("_")], leg[1]
                        fromstopidx = stops_dict[trip_route].index(journey_final_copy[c - 1][2])
                        journey_final.append([leg[0], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]])
                    elif journey_final_copy[c - 1][0] == "trip":
                        [trip_route, numb], tostopidx = [int(x) for x in leg[0].split("_")], leg[1]
                        fromstopidx = stops_dict[trip_route].index(SOURCE)
                        if [leg[0], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]] not in journey_final:
                            journey_final.append([leg[0], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]])
                from_stop = stops_dict[int(journey_final_copy[c][0].split("_")[0])][int(journey_final_copy[c][1])]
                to_stop = stops_dict[int(journey_final_copy[c][2].split("_")[0])][int(journey_final_copy[c][3])]
                if from_stop != to_stop:
                    time_needed = [x[1] for x in footpath_dict[from_stop] if x[0] == to_stop][0]
                    journey_final.append(("walk", from_stop, to_stop, time_needed))
                    if c + 1 != len(journey_final_copy) - 1:
                        [trip_route, numb], fromstopidx = [int(x) for x in leg[2].split("_")], leg[3]
                        journey_final.append(
                            [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][1]]])
                elif from_stop == to_stop:
                    if c + 1 != len(journey_final_copy) - 1:
                        [trip_route, numb], fromstopidx = [int(x) for x in leg[2].split("_")], leg[3]
                        journey_final.append(
                            [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][1]]])
        for leg in journey_final:
            if leg[0] == "walk":
                print(f"from {leg[1]} walk till  {leg[2]} for {leg[3].total_seconds()} seconds")
            else:
                print(f"from {leg[1][0]} board at {leg[1][1].time()} and get down on {leg[2][0]} at {leg[2][1].time()} along {leg[0]}")
        print("####################################")
    return None


def _print_tbtr_journey_otm(J: dict, Q: list, DESTINATION: int, SOURCE: int, footpath_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                            D_TIME, MAX_TRANSFER: int, trip_transfer_dict: dict, rounds_desti_reached: list) -> None:
    """
    Prints the output of TBTR

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        DESTINATION (int): stop id of destination stop.
        SOURCE (int): stop id of source stop.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        D_TIME (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples
        rounds_desti_reached (list): Rounds in which DESTINATION is reached.

    Returns:
        None

    Examples:
        >>> _print_tbtr_journey(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, D_TIME, MAX_TRANSFER, trip_transfer_dict, rounds_desti_reached)

    TODO:
        Build a better backtracking system for TBTR
    """
    for x in reversed(rounds_desti_reached):
        round_no = x
        journey = []
        trip_segement_counter = J[DESTINATION][x][1][2]
        while round_no > 0:
            pred = Q[round_no][trip_segement_counter]
            journey.append((pred[5][0], pred[1], pred[0]))
            trip_segement_counter = pred[5][1]
            round_no = round_no - 1
        from_stop_list = []
        for id, t_transfer in enumerate(journey[:-1]):
            from_Stop_onwards = journey[id + 1][2]
            for from_stop, trasnsfer_list in trip_transfer_dict[t_transfer[0]].items():
                if from_stop < from_Stop_onwards:
                    continue
                else:
                    if (t_transfer[1], t_transfer[2]) in trasnsfer_list:
                        from_stop_list.append(from_stop)
        journey_final = [(journey[counter][0], x, journey[counter][1], journey[counter][2]) for counter, x in enumerate(from_stop_list)]
        # from source
        from_trip, from_stop_idxx = journey[-1][1], journey[-1][2]
        fromstopid = stops_dict[int(from_trip.split("_")[0])][from_stop_idxx]
        if fromstopid == SOURCE:
            journey_final.append(("trip", 0, from_trip, from_stop_idxx))
        else:
            for to_stop, to_time in footpath_dict[fromstopid]:
                if to_stop == SOURCE:
                    journey_final.append(("walk", SOURCE, fromstopid, to_time + D_TIME))
                    break
        # Add final lag. Destination can either be along the route or at a walking distance from it.
        if J[DESTINATION][x][1][1] != (0, 0):  # Add here if the destination is at walking distance from final route
            try:
                final_route, boarded_from = int(journey_final[0][2].split("_")[0]), journey_final[0][3]
                found = 0
                for walking_from_stop_idx, stop_id in enumerate(stops_dict[final_route]):
                    if walking_from_stop_idx < boarded_from: continue
                    try:
                        for to_stop, to_stop_time in footpath_dict[stop_id]:
                            if to_stop == DESTINATION:
                                found = 1
                                journey_final.insert(0, ("walk", journey_final[0][2], boarded_from, walking_from_stop_idx,
                                                         to_stop_time))  # walking_pointer, from_trip, from_stop, to_stop
                                break
                    except KeyError:
                        continue
                    if found == 1: break
            except AttributeError:
                if len(journey_final) == 1:
                    final_route = int(J[DESTINATION][x][1][0].split("_")[0])
                    boarded_from = stops_dict[final_route].index(journey_final[0][2])
                    found = 0
                    for walking_from_stop_idx, stop_id in enumerate(stops_dict[final_route]):
                        if walking_from_stop_idx < boarded_from: continue
                        try:
                            for to_stop, to_stop_time in footpath_dict[stop_id]:
                                if to_stop == DESTINATION:
                                    found = 1
                                    journey_final.insert(0, ("walk", J[DESTINATION][x][1][0], boarded_from, walking_from_stop_idx,
                                                             to_stop_time))  # walking_pointer, from_trip, from_stop, to_stop
                                    break
                        except KeyError:
                            continue
                        if found == 1: break
                else:
                    raise NameError
        else:  # Destination is along the route.
            try:
                final_route, boarded_from = int(journey_final[0][2].split("_")[0]), journey_final[0][3]
                desti_index = stops_dict[final_route].index(DESTINATION)
                journey_final.insert(0, ("trip", journey_final[0][2], boarded_from, desti_index))  # walking_pointer, from_trip, from_stop, to_stop
            except AttributeError:
                if len(journey_final) == 1:
                    final_route = int(J[DESTINATION][x][1][0].split("_")[0])
                    boarded_from = stops_dict[final_route].index(journey_final[0][2])
                    desti_index = stops_dict[final_route].index(DESTINATION)
                    journey_final.insert(0, ("trip", J[x][1][0], boarded_from, desti_index))  # walking_pointer, from_trip, from_stop, to_stop
        if journey_final == []:
            tid = [int(x) for x in journey[0][1].split("_")]
            tostop_det = stops_dict[tid[0]].index(DESTINATION)
            journey_final.append((journey[0][1], stoptimes_dict[tid[0]][tid[1]][journey[0][2]], stoptimes_dict[tid[0]][tid[1]][tostop_det]))
        journey_final.reverse()
        journey_final_copy = journey_final.copy()
        journey_final.clear()
        for c, leg in enumerate(journey_final_copy):
            if c == 0:
                if leg[0] == "trip":
                    [trip_route, numb], fromstopidx = [int(x) for x in leg[2].split("_")], leg[3]
                    try:
                        journey_final.append(
                            [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][1]]])
                    except TypeError:
                        try:
                            journey_final.append([leg[2], stoptimes_dict[trip_route][numb][fromstopidx],
                                                  stoptimes_dict[trip_route][numb][stops_dict[trip_route].index(DESTINATION)]])
                            break
                        except ValueError:
                            journey_final.append(
                                [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][3]]])
                elif leg[0] == "walk":
                    journey_final.append(("walk", leg[1], leg[2], [time for stop, time in footpath_dict[leg[1]] if stop == leg[2]][0]))
            elif c == len(journey_final_copy) - 1:
                if leg[0] == "trip":
                    [trip_route, numb], fromstopidx, tostopidx = [int(x) for x in leg[1].split("_")], leg[2], leg[3]
                    journey_final.append([leg[1], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]])
                elif leg[0] == "walk":
                    from_trip = [int(x) for x in leg[1].split("_")]
                    journey_final.append((leg[1], stoptimes_dict[from_trip[0]][from_trip[1]][leg[2]], stoptimes_dict[from_trip[0]][from_trip[1]][leg[3]]))
                    foot_connect = stoptimes_dict[from_trip[0]][from_trip[1]][leg[3]]
                    last_foot_tme = [time for stop, time in footpath_dict[foot_connect[0]] if stop == DESTINATION][0]
                    journey_final.append(
                        ("walk", foot_connect[0], DESTINATION, last_foot_tme, stoptimes_dict[from_trip[0]][from_trip[1]][leg[3]][1] + last_foot_tme))
            else:
                if c == 1:
                    if journey_final_copy[c - 1][0] == "walk":
                        [trip_route, numb], tostopidx = [int(x) for x in leg[0].split("_")], leg[1]
                        fromstopidx = stops_dict[trip_route].index(journey_final_copy[c - 1][2])
                        journey_final.append([leg[0], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]])
                    elif journey_final_copy[c - 1][0] == "trip":
                        [trip_route, numb], tostopidx = [int(x) for x in leg[0].split("_")], leg[1]
                        fromstopidx = stops_dict[trip_route].index(SOURCE)
                        if [leg[0], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]] not in journey_final:
                            journey_final.append([leg[0], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][tostopidx]])
                from_stop = stops_dict[int(journey_final_copy[c][0].split("_")[0])][int(journey_final_copy[c][1])]
                to_stop = stops_dict[int(journey_final_copy[c][2].split("_")[0])][int(journey_final_copy[c][3])]
                if from_stop != to_stop:
                    time_needed = [x[1] for x in footpath_dict[from_stop] if x[0] == to_stop][0]
                    journey_final.append(("walk", from_stop, to_stop, time_needed))
                    if c + 1 != len(journey_final_copy) - 1:
                        [trip_route, numb], fromstopidx = [int(x) for x in leg[2].split("_")], leg[3]
                        journey_final.append(
                            [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][1]]])
                elif from_stop == to_stop:
                    if c + 1 != len(journey_final_copy) - 1:
                        [trip_route, numb], fromstopidx = [int(x) for x in leg[2].split("_")], leg[3]
                        journey_final.append(
                            [leg[2], stoptimes_dict[trip_route][numb][fromstopidx], stoptimes_dict[trip_route][numb][journey_final_copy[c + 1][1]]])
        for leg in journey_final:
            if leg[0] == "walk":
                print(f"from {leg[1]} walk till  {leg[2]} for {leg[3].total_seconds()} seconds")
            else:
                print(f"from {leg[1][0]} board at {leg[1][1].time()} and get down on {leg[2][0]} at {leg[2][1].time()} along {leg[0]}")
        print("####################################")
    return None
