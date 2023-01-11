"""
Module contains function related to transfer patterns, scalable transfer patterns
"""
import itertools
import pickle
from collections import Counter, defaultdict, deque

import networkx as nx
import pandas as pd
from tqdm import tqdm


def initialize_onemany_tbtr(MAX_TRANSFER, DESTINATION_LIST) -> tuple:
    '''
    Initialize values for one-to-many TBTR.

    Args:
        MAX_TRANSFER (int): maximum transfer limit.
        DESTINATION_LIST (list): list of stop ids of destination stop.

    Returns:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time.
        inf_time (pandas.datetime): Variable indicating infinite time.
    '''
    #    inf_time = pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")
    inf_time = pd.to_datetime("2023-01-26 20:00:00")
    J = {desti: {x: [inf_time, 0] for x in range(MAX_TRANSFER + 1)} for desti in DESTINATION_LIST}
    return J, inf_time


def initialize_from_desti_onemany_tbtr(routes_by_stop_dict, stops_dict, DESTINATION_LIST, footpath_dict, idx_by_route_stop_dict) -> dict:
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


def update_label_tbtr(label, no_of_transfer, predecessor_label, J, MAX_TRANSFER) -> dict:
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


def initialize_from_source_range_tbtr(dep_details, MAX_TRANSFER, stoptimes_dict, R_t) -> list:
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
    enqueue_range_tbtr(connection_list, 1, (0, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
    return Q


def enqueue_range_tbtr(connection_list, nextround, predecessor_label, R_t, Q, stoptimes_dict, MAX_TRANSFER) -> None:
    '''
    adds trips-segments to next round round and update R_t. Used in range queries

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
    return None


def post_process_range_onemany_tbtr(J, Q, rounds_desti_reached, PRINT_ITINERARY, desti, SOURCE, footpath_dict,
                                    stops_dict, stoptimes_dict, d_time, MAX_TRANSFER, trip_transfer_dict) -> list:
    '''
    Contains all the post-processing features for One-To-Many rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal journeys.

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        rounds_desti_reached (list): Rounds in which DESTINATION is reached.
        desti (int): destination stop id.

    Returns:
        TBTR_out (set): Trips needed to cover pareto-optimal journeys.
    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    TP = _print_tbtr_journey_otm(J, Q, desti, SOURCE, footpath_dict, stops_dict, stoptimes_dict, d_time, MAX_TRANSFER, trip_transfer_dict, rounds_desti_reached,
                                 PRINT_ITINERARY)
    return TP


def _print_tbtr_journey_otm(J: dict, Q: list, DESTINATION: int, SOURCE: int, footpath_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                            D_TIME, MAX_TRANSFER: int, trip_transfer_dict: dict, rounds_desti_reached: list, PRINT_ITINERARY: int) -> list:
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
         PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.            

    Returns:
         TP_list (list): list of transfer patterns
        
    """
    TP_list = []
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
                    journey_final.insert(0, ("trip", J[DESTINATION][x][1][0], boarded_from, desti_index))  # walking_pointer, from_trip, from_stop, to_stop
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
        TP = []
        for leg in journey_final:
            if leg[0] == "walk":
                if PRINT_ITINERARY == 1: print(f"from {leg[1]} walk till  {leg[2]} for {leg[3].total_seconds()} seconds")
                TP.extend([leg[1], leg[2]])
            else:
                if PRINT_ITINERARY == 1: print(f"from {leg[1][0]} board at {leg[1][1].time()} and get down on {leg[2][0]} at {leg[2][1].time()} along {leg[0]}")
                TP.extend([leg[1][0], leg[2][0]])
        TP_list.append(list(dict.fromkeys(TP)))
        if PRINT_ITINERARY == 1: print("####################################")
    return TP_list


def onetomany_rtbtr_forhubs(SOURCE: int, DESTINATION_LIST: list, d_time_groups, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int,
                            PRINT_ITINERARY: int, OPTIMIZED: int, routes_by_stop_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                            footpath_dict: dict, idx_by_route_stop_dict: dict, trip_transfer_dict: dict, trip_set: set, hubstops: set) -> list:
    """
    One to many rTBTR implementation. Connections are not added from the stops in hubstops set.

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION_LIST (list): list of stop ids of destination stop.
        d_time_groups (pandas.group): all possible departures times from all stops.
        MAX_TRANSFER (int): maximum transfer limit.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples
        of form (id of trip we are transferring to, stop number)}
        trip_set (set): set of trip ids from which trip-transfers are available.
        hubstops (set): set containing id's of stop that are hubs

    Returns:
        if OPTIMIZED==1:
            out (list):  list of trips required to cover all optimal journeys Format: [trip_id]
        elif OPTIMIZED==0:
            out (list):  list of routes required to cover all optimal journeys. Format: [route_id]
    """
    DESTINATION_LIST.remove(SOURCE)
    d_time_list = d_time_groups.get_group(SOURCE)[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist()
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                d_time_list.extend(d_time_groups.get_group(connection[0])[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist())
        except KeyError:
            pass
    d_time_list.sort(key=lambda x: x[1], reverse=True)

    TP_list = []
    J, inf_time = initialize_onemany_tbtr(MAX_TRANSFER, DESTINATION_LIST)
    L = initialize_from_desti_onemany_tbtr(routes_by_stop_dict, stops_dict, DESTINATION_LIST, footpath_dict, idx_by_route_stop_dict)
    R_t = {x: defaultdict(lambda: 1000) for x in range(0, MAX_TRANSFER + 2)}  # assuming maximum route length is 1000

    for dep_details in d_time_list:
        rounds_desti_reached = {x: [] for x in DESTINATION_LIST}
        n = 1
        Q = initialize_from_source_range_tbtr(dep_details, MAX_TRANSFER, stoptimes_dict, R_t)
        dest_list_prime = DESTINATION_LIST.copy()
        while n <= MAX_TRANSFER:
            stop_mark_dict = {stop: 0 for stop in dest_list_prime}
            scope = []
            for counter, trip_segment in enumerate(Q[n]):
                from_stop, tid, to_stop, trip_route, tid_idx = trip_segment[0: 5]
                trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
                connection_list = []
                for desti in dest_list_prime:
                    try:
                        L[desti][trip_route]
                        stop_list, _ = zip(*trip)
                        for last_leg in L[desti][trip_route]:
                            idx = [x[0] for x in enumerate(stop_list) if x[1] == last_leg[2]]
                            if idx and from_stop < last_leg[0] and trip[idx[0]][1] + last_leg[1] < J[desti][n][0]:
                                if last_leg[1] == pd.to_timedelta(0, unit="seconds"):
                                    walking = (0, 0)
                                else:
                                    walking = (1, stops_dict[trip_route][last_leg[0]])
                                J[desti] = update_label_tbtr(trip[idx[0]][1] + last_leg[1], n, (tid, walking, counter), J[desti], MAX_TRANSFER)
                                rounds_desti_reached[desti].append(n)
                    except KeyError:
                        pass
                    try:
                        if tid in trip_set and trip[1][1] < J[desti][n][0]:
                            if stop_mark_dict[desti] == 0:
                                scope.append(desti)
                                stop_mark_dict[desti] = 1
                            connection_list.extend(
                                [connection for from_stop_idx, transfer_stop_id in enumerate(trip[1:], from_stop + 1) if transfer_stop_id[0] not in hubstops
                                 for connection in trip_transfer_dict[tid][from_stop_idx]])
                    except IndexError:
                        pass
                connection_list = list(set(connection_list))
                enqueue_range_tbtr(connection_list, n + 1, (tid, counter, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
            dest_list_prime = [*scope]
            n = n + 1
        for desti in DESTINATION_LIST:
            if rounds_desti_reached[desti]:
                TP_list.extend(
                    post_process_range_onemany_tbtr(J, Q, rounds_desti_reached[desti], PRINT_ITINERARY, desti, SOURCE, footpath_dict, stops_dict,
                                                    stoptimes_dict,
                                                    dep_details[1], MAX_TRANSFER, trip_transfer_dict))
    return TP_list


def build_query_graph(SOURCE, NETWORK_NAME, hub_count, hubstops) -> dict:
    """
    Builds the query graph for transfer patterns.

    Args:
        SOURCE (int): stop id of source stop.
        NETWORK_NAME (str): GTFS path
        hub_count (int):  Number of hub stops
        hubstops (set): set containing id's of stop that are hubs

    Returns:
        adj_list (dist): adjacency list for the query graph

    """
    with open(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_{hub_count}/{SOURCE}", "rb") as fp:  # Unpickling
        stored_transferpattern = pickle.load(fp)
    for hub in hubstops:
        with open(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_{hub_count}/{hub}", "rb") as fp:  # Unpickling
            stored_transferpattern.extend(pickle.load(fp))

    edge_list = [(edge[x], edge[x + 1]) for edge in stored_transferpattern for x in range(len(edge) - 1)]
    G = nx.DiGraph()
    G.add_edges_from(edge_list)
    adj_list = {int(x.split(',')[0]): [[int(x) for x in x.split(',')[1:]], [], []] for x in list(nx.generate_adjlist(G, delimiter=','))}
    return adj_list


def build_query_graph_forSTP(SOURCE, DESTINATION, NETWORK_NAME, cluster_info) -> dict:
    """
    Builds the query graph for scalable transfer patterns.

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        NETWORK_NAME (str): GTFS path
        cluster_info:

    Returns:
        adj_list (dist): adjacency list for the query graph

    """
    cluster_count = len(cluster_info.keys()) - 1
    is_source_border, is_desti_border = False, False
    for cid in range(0, cluster_count):
        if SOURCE in cluster_info[cid]:
            s_cid = cid
    if SOURCE in cluster_info[-1]:
        is_source_border = True
    for cid in range(0, cluster_count):
        if DESTINATION in cluster_info[cid]:
            d_cid = cid
    if DESTINATION in cluster_info[-1]:
        is_desti_border = True
    if s_cid == d_cid or is_desti_border == is_source_border == True:
        with open(f"./TRANSFER_PATTERNS/stp/{NETWORK_NAME}_{cluster_count}/{SOURCE}", "rb") as fp:
            stored_transferpattern = pickle.load(fp)
        edge_list = list(set([(edge[x], edge[x + 1]) for edge in stored_transferpattern for x in range(len(edge) - 1)]))
    if s_cid != d_cid:
        with open(f"./TRANSFER_PATTERNS/stp/{NETWORK_NAME}_{cluster_count}/{SOURCE}", "rb") as fp:
            stored_transferpattern = pickle.load(fp)
        edge_list = list(set([(edge[x], edge[x + 1]) for edge in stored_transferpattern for x in range(len(edge) - 1)]))
        border_stops_of_source = cluster_info[s_cid].intersection(cluster_info[-1])
        for bordernode in border_stops_of_source:
            with open(f"./TRANSFER_PATTERNS/stp/{NETWORK_NAME}_{cluster_count}/{bordernode}", "rb") as fp:
                temp = list(set([(edge[x], edge[x + 1]) for edge in pickle.load(fp) for x in range(len(edge) - 1)]))
                edge_list.extend(temp)
        border_stops_of_destination = cluster_info[d_cid].intersection(cluster_info[-1])
        for bordernode in border_stops_of_destination:
            with open(f"./TRANSFER_PATTERNS/stp/{NETWORK_NAME}_{cluster_count}/{bordernode}", "rb") as fp:
                temp = list(set([(edge[x], edge[x + 1]) for edge in pickle.load(fp) for x in range(len(edge) - 1)]))
                edge_list.extend(temp)
    G = nx.DiGraph()
    G.add_edges_from(edge_list)
    adj_list = {int(x.split(',')[0]): [[int(x) for x in x.split(',')[1:]], [], []] for x in list(nx.generate_adjlist(G, delimiter=','))}
    return adj_list


def check_dominance(t_l, adjlist_dict, DESTINATION) -> bool:
    """
    Check if the best values in both the criteria is dominated by destination

    Args:
        t_l (list): list of tuples of format: (arrival time, number of transfer, predecessor node id, index of label updated from, self node_id)
        adj_list (dist): adjacency list for the query graph
        DESTINATION (int): stop id of destination stop.

    Returns:
        True or False (boolean)

    """
    first_crit, second_crit, _, _, _ = zip(*t_l)
    minimum_t_l = [min(first_crit), min(second_crit)]
    desti_critera = [(label[0], label[1]) for label in adjlist_dict[DESTINATION][2]]
    for label in desti_critera:
        if minimum_t_l[0] >= label[0] and minimum_t_l[1] >= label[1]:
            # print("Terminted early")
            return False
    return True


def new_label_is_dominated(new_label, adjlist_dict, DESTINATION) -> bool:
    """
    Check if the new_label dominates the destination label

    Args:
        new_label (list): list of tuples of format: (arrival time, number of transfer, predecessor node id, index of label updated from, self node_id)
        adj_list (dist): adjacency list for the query graph
        DESTINATION (int): stop id of destination stop.

    Returns:
        True or False (boolean)

    """

    desti_critera = [(label[0], label[1]) for label in adjlist_dict[DESTINATION][2]]
    for label in desti_critera:
        if new_label[0] >= label[0] and new_label[1] >= label[1]:
            # print("label not evaluated")
            return True
    return False


def multicriteria_dij_alternate(SOURCE: int, DESTINATION: int, D_TIME, footpath_dict: dict, NETWORK_NAME: str, routesindx_by_stop_dict: dict,
                                stoptimes_dict: dict, hub_count: int, hubstops: set) -> dict:
    """
    Multicriteria Dijkstra's algorithm to be used in transfer patterns query phase. The implementation has been borrowed from NetworkX.
    This is untested-varient of Martin's algorithm

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        NETWORK_NAME (str): GTFS path
        routesindx_by_stop_dict (dict): Keys: stop id, value: [(route_id, stop index), (route_id, stop index)]
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        hub_count (int):  Number of hub stops
        hubstops (set): set containing id's of stop that are hubs

    Returns:
        adj_list (dist): adjacency list for the query graph

    #TODO: Check correctness and efficiency
    """

    adjlist_dict = build_query_graph(SOURCE, NETWORK_NAME, hub_count, hubstops)
    t_l = []
    init_label = [D_TIME, 0, 0, 0, SOURCE]  # criteria1, criteria2, pred_node_id, idx_predece_label, self.node_id

    t_l.append(init_label)
    adjlist_dict[SOURCE][1].append(init_label)

    while (t_l and check_dominance(t_l, adjlist_dict, DESTINATION)):
        # while (t_l):

        l_q = min(t_l)
        q = l_q[4]

        # Move l_q from temporary to permanent
        t_l.remove(l_q)
        adjlist_dict[q][1].remove(l_q)
        adjlist_dict[q][2].append(l_q)

        h = adjlist_dict[q][2].index(l_q)  # Store the position of label l_q from l_pq
        for j in adjlist_dict[q][0]:
            # Compute l_j the current label of vertex j
            try:
                arr_time = arrivaltme_query(q, j, l_q[0], routesindx_by_stop_dict, stoptimes_dict)
            except ValueError:
                continue  # No trip avaliable after l_q[0]
            l_j = list((arr_time, l_q[1] + 1, q, h, j))

            # Verify there is no label of j dominated by l_j
            dominated = False
            for label in adjlist_dict[j][1] + adjlist_dict[j][2]:
                if label[0] <= l_j[0] and label[1] <= l_j[1]:
                    dominated = True
                    break

            if dominated == False:
                # Store l_j as temporary label of j
                adjlist_dict[j][1].append(l_j)
                t_l.append(l_j)
                # Delete all temporary labels of j dominated by l_j
                for label in adjlist_dict[j][1]:
                    if l_j[0] == label[0] and l_j[1] == label[1]:
                        continue
                    if l_j[0] <= label[0] and l_j[1] <= label[1]:
                        adjlist_dict[j][1].remove(label)
                        t_l.remove(label)
        try:
            for j, footpath_time in footpath_dict[q]:
                l_j = list((l_q[0] + footpath_time, l_q[1], q, h, j))

                # Verify there is no label of j dominated by l_j
                dominated = False
                for label in adjlist_dict[j][1] + adjlist_dict[j][2]:
                    if label[0] <= l_j[0] and label[1] <= l_j[1]:
                        dominated = True
                        break

                if dominated == False:
                    # Store l_j as temporary label of j
                    adjlist_dict[j][1].append(l_j)
                    t_l.append(l_j)
                    # Delete all temporary labels of j dominated by l_j
                    for label in adjlist_dict[j][1]:
                        if l_j[0] == label[0] and l_j[1] == label[1]:
                            continue
                        if l_j[0] <= label[0] and l_j[1] <= label[1]:
                            adjlist_dict[j][1].remove(label)
                            t_l.remove(label)
        except KeyError:
            pass
    return adjlist_dict


def multicriteria_dij(SOURCE: int, DESTINATION: int, D_TIME, footpath_dict: dict, NETWORK_NAME: str, routesindx_by_stop_dict: dict, stoptimes_dict: dict,
                      hub_count: int, hubstops: set) -> dict:
    """
    Multicriteria Dijkstra's algorithm to be used in transfer patterns query phase. The implementation has been borrowed from NetworkX.

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        NETWORK_NAME (str): GTFS path
        routesindx_by_stop_dict (dict): Keys: stop id, value: [(route_id, stop index), (route_id, stop index)]
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        hub_count (int):  Number of hub stops
        hubstops (set): set containing id's of stop that are hubs

    Returns:
        adj_list (dist): adjacency list for the query graph

    """
    adjlist_dict = build_query_graph(SOURCE, NETWORK_NAME, hub_count, hubstops)
    t_l = []
    init_label = [D_TIME, 0, 0, 0, SOURCE]  # criteria1, criteria2, pred_node_id, idx_predece_label, self.node_id

    t_l.append(init_label)
    adjlist_dict[SOURCE][1].append(init_label)

    # while (t_l and check_dominance(t_l, adjlist_dict, DESTINATION)):
    while (t_l):

        l_q = min(t_l)
        q = l_q[4]

        # Move l_q from temporary to permanent
        t_l.remove(l_q)
        adjlist_dict[q][1].remove(l_q)
        adjlist_dict[q][2].append(l_q)
        if new_label_is_dominated(l_q, adjlist_dict, DESTINATION):
            continue
        h = adjlist_dict[q][2].index(l_q)  # Store the position of label l_q from l_pq
        for j in adjlist_dict[q][0]:
            # Compute l_j the current label of vertex j
            try:
                arr_time = arrivaltme_query(q, j, l_q[0], routesindx_by_stop_dict, stoptimes_dict)
            except ValueError:
                continue  # No trip avaliable after l_q[0]
            l_j = list((arr_time, l_q[1] + 1, q, h, j))

            # Verify there is no label of j dominated by l_j
            dominated = False
            for label in adjlist_dict[j][1] + adjlist_dict[j][2]:
                if label[0] <= l_j[0] and label[1] <= l_j[1]:
                    dominated = True
                    break

            if dominated == False:
                # Store l_j as temporary label of j
                adjlist_dict[j][1].append(l_j)
                t_l.append(l_j)
                # Delete all temporary labels of j dominated by l_j
                for label in adjlist_dict[j][1]:
                    if l_j[0] == label[0] and l_j[1] == label[1]:
                        continue
                    if l_j[0] <= label[0] and l_j[1] <= label[1]:
                        adjlist_dict[j][1].remove(label)
                        t_l.remove(label)
        try:
            for j, footpath_time in footpath_dict[q]:
                l_j = list((l_q[0] + footpath_time, l_q[1], q, h, j))

                # Verify there is no label of j dominated by l_j
                dominated = False
                for label in adjlist_dict[j][1] + adjlist_dict[j][2]:
                    if label[0] <= l_j[0] and label[1] <= l_j[1]:
                        dominated = True
                        break

                if dominated == False:
                    # Store l_j as temporary label of j
                    adjlist_dict[j][1].append(l_j)
                    t_l.append(l_j)
                    # Delete all temporary labels of j dominated by l_j
                    for label in adjlist_dict[j][1]:
                        if l_j[0] == label[0] and l_j[1] == label[1]:
                            continue
                        if l_j[0] <= label[0] and l_j[1] <= label[1]:
                            adjlist_dict[j][1].remove(label)
                            t_l.remove(label)
        except KeyError:
            pass
    return adjlist_dict


def multicriteria_dij_forSTP(SOURCE: int, DESTINATION: int, D_TIME, footpath_dict: dict, NETWORK_NAME: str, routesindx_by_stop_dict: dict, stoptimes_dict: dict,
                             cluster_info) -> dict:
    """
    Multicriteria Dijkstra's algorithm to be used in scalable transfer patterns query phase. The implementation has been borrowed from NetworkX.

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        NETWORK_NAME (str): GTFS path
        routesindx_by_stop_dict (dict): Keys: stop id, value: [(route_id, stop index), (route_id, stop index)]
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        cluster_info:

    Returns:
        adj_list (dist): adjacency list for the query graph

    """

    adjlist_dict = build_query_graph_forSTP(SOURCE, DESTINATION, NETWORK_NAME, cluster_info)
    t_l = []
    init_label = [D_TIME, 0, 0, 0, SOURCE]  # criteria1, criteria2, pred_node_id, idx_predece_label, self.node_id

    t_l.append(init_label)
    adjlist_dict[SOURCE][1].append(init_label)
    # adjlist_dict[33991]
    while t_l:
        l_q = min(t_l)
        q = l_q[4]

        # Move l_q from temporary to permanent
        t_l.remove(l_q)
        adjlist_dict[q][1].remove(l_q)
        adjlist_dict[q][2].append(l_q)

        h = adjlist_dict[q][2].index(l_q)  # Store the position of label l_q from l_pq
        for j in adjlist_dict[q][0]:
            # Compute l_j the current label of vertex j
            try:
                arr_time = arrivaltme_query(q, j, l_q[0], routesindx_by_stop_dict, stoptimes_dict)
            except ValueError:
                continue  # No trip avaliable after l_q[0]
            l_j = list((arr_time, l_q[1] + 1, q, h, j))

            # Verify there is no label of j dominated by l_j
            dominated = False
            for label in adjlist_dict[j][1] + adjlist_dict[j][2]:
                if label[0] <= l_j[0] and label[1] <= l_j[1]:
                    dominated = True
                    break

            if dominated == False:
                # Store l_j as temporary label of j
                adjlist_dict[j][1].append(l_j)
                t_l.append(l_j)
                # Delete all temporary labels of j dominated by l_j
                for label in adjlist_dict[j][1]:
                    if l_j[0] == label[0] and l_j[1] == label[1]:
                        continue
                    if l_j[0] <= label[0] and l_j[1] <= label[1]:
                        adjlist_dict[j][1].remove(label)
                        t_l.remove(label)
        try:
            for j, footpath_time in footpath_dict[q]:
                l_j = list((l_q[0] + footpath_time, l_q[1], q, h, j))

                # Verify there is no label of j dominated by l_j
                dominated = False
                for label in adjlist_dict[j][1] + adjlist_dict[j][2]:
                    if label[0] <= l_j[0] and label[1] <= l_j[1]:
                        dominated = True
                        break

                if dominated == False:
                    # Store l_j as temporary label of j
                    adjlist_dict[j][1].append(l_j)
                    t_l.append(l_j)
                    # Delete all temporary labels of j dominated by l_j
                    for label in adjlist_dict[j][1]:
                        if l_j[0] == label[0] and l_j[1] == label[1]:
                            continue
                        if l_j[0] <= label[0] and l_j[1] <= label[1]:
                            adjlist_dict[j][1].remove(label)
                            t_l.remove(label)
        except KeyError:
            pass
    return adjlist_dict


def arrivaltme_query(stop1: int, stop2: int, deptime, routesindx_by_stop_dict: dict, stoptimes_dict: dict):
    """
    Find the earliest trip departing from stop 1 after deptime and going to stop 2.

    Args:
        stop1 (int): Stop id
        stop2 (int): Stop id
        deptime (pandas.datetime):
        routesindx_by_stop_dict (dict): Keys: stop id, value: [(route_id, stop index), (route_id, stop index)]
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.

    Returns:
        pandas.datetime object

    """
    routeidx1, routeidx2 = routesindx_by_stop_dict[stop1], routesindx_by_stop_dict[stop2]
    comon_routes = [(seq1, seq2) for seq1, seq2 in itertools.product(routeidx1, routeidx2) if seq1[0] == seq2[0] and seq1[1] < seq2[1]]
    arrival_times = []
    for iternary in comon_routes:
        for trip_idx, trip in enumerate(stoptimes_dict[iternary[0][0]]):
            if trip[iternary[0][1]][1] >= deptime:
                arrival_times.append(trip[iternary[1][1]][1])
                break
    return min(arrival_times)


def get_brutehubs(routes_by_stop_dict, NETWORK_NAME) -> list:
    """
    Select hubs using brute force. This is Naive implementation that can be used to test the effectiveness of the hubs. The idea is to generate
    full transfer patterns (without hubs) and then use optimal paths to find hub stops.

    Args:
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        NETWORK_NAME (str): GTFS path

    Returns:
        global_count (list): list of tuples of format: (stop_id, number of optimal paths it stop_id is belongs to)

    """
    global_count = Counter({x: 0 for x in routes_by_stop_dict.keys()})
    for stop_id in tqdm(routes_by_stop_dict.keys()):
        with open(f"./TRANSFER_PATTERNS/{NETWORK_NAME}_0/{stop_id}", "rb") as fp:  # Unpickling
            temp = Counter([item for sublist in pickle.load(fp) for item in sublist])
        global_count = global_count + temp
    global_count = sorted(dict(global_count).items(), key=lambda x: x[1], reverse=True)
    hub_dict = {hubs: [x for x, y in global_count[:hubs]] for hubs in [25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800]}
    hub_dict[0] = []
    with open(f'./TRANSFER_PATTERNS/{NETWORK_NAME}_hub_brute.pkl', 'wb') as pickle_file:
        pickle.dump(hub_dict, pickle_file)
    return global_count


def onetoall_rraptor_forhubs(SOURCE: int, DESTINATION_LIST: list, d_time_groups, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int, CHANGE_TIME_SEC: int,
                             PRINT_ITINERARY: int, OPTIMIZED: int, routes_by_stop_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                             footpath_dict: dict, idx_by_route_stop_dict: dict, hubstops: set) -> list:
    """
    One-To-Many rRAPTOR implementation. Trips are not scanned from the stops in hubstops set.

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION_LIST (list): list of stop ids of destination stop.
        d_time_groups (pandas.group): all possible departures times from all stops.
        MAX_TRANSFER (int): maximum transfer limit.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        CHANGE_TIME_SEC (int): change-time in seconds.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.
        hubstops (set): set containing id's of stop that are hubs

    Returns:
        if OPTIMIZED==1:
            out (list):  list of trips required to cover all optimal journeys Format: [trip_id]
        elif OPTIMIZED==0:
            out (list):  list of routes required to cover all optimal journeys. Format: [route_id]

    Examples:
        >>> output = onetomany_rraptor(36, [52, 43], pd.to_datetime('2019-06-10 00:00:00'), 4, 1, 0, 1, 0, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict)

    """
    try:
        DESTINATION_LIST.remove(SOURCE)
    except ValueError:
        pass
    # d_time_list is list tuples. Format = [(trip_id, arrival time, stop index)]
    d_time_list = d_time_groups.get_group(SOURCE)[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist()
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                d_time_list.extend(d_time_groups.get_group(connection[0])[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist())
        except KeyError:
            pass
    d_time_list.sort(key=lambda x: x[1], reverse=True)
    _, _, label, _, star_label, inf_time = initialize_raptor(routes_by_stop_dict, SOURCE, MAX_TRANSFER)
    change_time = pd.to_timedelta(CHANGE_TIME_SEC, unit='seconds')
    output = []
    for dep_details in d_time_list:
        pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, MAX_TRANSFER + 1)}
        marked_stop = deque()
        marked_stop_dict = {stop: 0 for stop in routes_by_stop_dict.keys()}
        start_tid, d_time, s_idx = dep_details
        first_stop = stops_dict[int(start_tid.split("_")[0])][s_idx]
        if first_stop != SOURCE:
            marked_stop.append(first_stop)
            marked_stop_dict[first_stop] = 1
            to_pdash_time = [foot_connect[1] for foot_connect in footpath_dict[SOURCE] if foot_connect[0] == first_stop][0]
            label[0][first_stop] = d_time - change_time
            star_label[first_stop] = d_time - change_time
            pi_label[0][first_stop] = ('walking', SOURCE, first_stop, to_pdash_time, d_time - change_time)
        else:
            marked_stop.append(SOURCE)
            marked_stop_dict[SOURCE] = 1
            (label[0][SOURCE], star_label[SOURCE]) = (d_time, d_time)
        if PRINT_ITINERARY == 1:
            print(SOURCE, d_time)
        Q = {}
        # Main code part 1
        for k in range(1, MAX_TRANSFER + 1):

            Q.clear()  # Format of Q is {route:stop}
            while marked_stop:
                p = marked_stop.pop()
                marked_stop_dict[p] = 0
                if k == 1:
                    Q[int(start_tid.split('_')[0])] = s_idx
                    break
                try:
                    routes_serving_p = routes_by_stop_dict[p]
                    for route in routes_serving_p:
                        stp_idx = idx_by_route_stop_dict[(route, p)]
                        if route in Q.keys() and Q[route] != stp_idx:
                            Q[route] = min(stp_idx, Q[route])
                        else:
                            Q[route] = stp_idx
                except KeyError:
                    continue
            # Main code part 2
            for route, current_stopindex_by_route in Q.items():
                current_trip_t = -1
                for p_i in stops_dict[route][current_stopindex_by_route:]:
                    if current_trip_t != -1 and current_trip_t[current_stopindex_by_route][1] < star_label[p_i]:
                        arr_by_t_at_pi = current_trip_t[current_stopindex_by_route][1]
                        label[k][p_i], star_label[p_i] = arr_by_t_at_pi, arr_by_t_at_pi
                        pi_label[k][p_i] = (boarding_time, boarding_point, p_i, arr_by_t_at_pi, tid)
                        if marked_stop_dict[p_i] == 0:
                            if p_i not in hubstops:
                                marked_stop.append(p_i)
                                marked_stop_dict[p_i] = 1
                    if current_trip_t == -1 or label[k - 1][p_i] + change_time < current_trip_t[current_stopindex_by_route][
                        1]:  # assuming arrival_time = departure_time
                        tid, current_trip_t = get_latest_trip_new(stoptimes_dict, route, label[k - 1][p_i], current_stopindex_by_route, change_time)
                        if current_trip_t == -1:
                            boarding_time, boarding_point = -1, -1
                        else:
                            boarding_point = p_i
                            boarding_time = current_trip_t[current_stopindex_by_route][1]
                    current_stopindex_by_route = current_stopindex_by_route + 1
            # Main code part 3
            marked_stop_copy = [*marked_stop]
            for p in marked_stop_copy:
                try:
                    trans_info = footpath_dict[p]
                    for i in trans_info:
                        (p_dash, to_pdash_time) = i
                        new_p_dash_time = label[k][p] + to_pdash_time
                        if new_p_dash_time < star_label[p_dash]:
                            label[k][p_dash], star_label[p_dash] = new_p_dash_time, new_p_dash_time
                            pi_label[k][p_dash] = ('walking', p, p_dash, to_pdash_time, new_p_dash_time)
                            if marked_stop_dict[p_dash] == 0:
                                if p_dash not in hubstops:
                                    marked_stop.append(p_dash)
                                    marked_stop_dict[p_dash] = 1
                except KeyError:
                    continue
            # Main code End
            if marked_stop == deque([]):
                # print('code ended with termination condition')
                break
        output.extend(post_processing_onetoall_rraptor(DESTINATION_LIST, pi_label, PRINT_ITINERARY, label, OPTIMIZED))
        if PRINT_ITINERARY == 1:
            print('------------------------------------')
    return output


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


def post_processing_onetoall_rraptor(DESTINATION_LIST: list, pi_label: dict, PRINT_ITINERARY: int, label: dict, OPTIMIZED: int) -> list:
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
    TP_list = []
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
            if PRINT_ITINERARY == 1:
                _print_Journey_legs(pareto_set)
            TP_list_desti = extract_transferpattern(pareto_set)
            TP_list.extend(TP_list_desti)
    return TP_list


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


def extract_transferpattern(pareto_journeys: list) -> list:
    '''
    Extract transfer patterns from pareto_journeys

    Args:
        pareto_journeys (list): pareto optimal set.

    Returns:
        pareto_journeys (list): list of stop sequence transfer patterns

    '''

    TP_list = []
    for _, journey in pareto_journeys:
        TP = []
        for leg in journey:
            if leg[0] == 'walking':
                TP.extend([int(leg[1]), int(leg[2])])
            else:
                TP.extend([int(leg[1]), int(leg[2])])
        TP_list.append(list(dict.fromkeys(TP)))
    return TP_list


"""
################################
Depreciated functions
################################


def post_process_range(J, Q, rounds_desti_reached, PRINT_ITINERARY, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, d_time, MAX_TRANSFER,
                       trip_transfer_dict) -> set:
    '''
    Contains all the post-processing features for rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal journeys.

    Args:
        J (dict): dict to store arrival timestamps. Keys: number of transfer, Values: arrival time
        Q (list): list of trips segments.
        rounds_desti_reached (list): Rounds in which DESTINATION is reached.

    Returns:
        necessory_trips (set): trips needed to cover pareto-optimal journeys.
    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    if PRINT_ITINERARY == 1:
        _print_tbtr_journey_otm(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, d_time, MAX_TRANSFER, trip_transfer_dict,
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



def onetomany_rtbtr(SOURCE: int, DESTINATION_LIST: list, d_time_groups, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int,
                    PRINT_ITINERARY: int, OPTIMIZED: int, routes_by_stop_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                    footpath_dict: dict, idx_by_route_stop_dict: dict, trip_transfer_dict: dict, trip_set: set) -> list:
    '''
    One to many rTBTR implementation

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION_LIST (list): list of stop ids of destination stop.
        d_time_groups (pandas.group): all possible departures times from all stops.
        MAX_TRANSFER (int): maximum transfer limit.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples
        of form (id of trip we are transferring to, stop number)}
        trip_set (set): set of trip ids from which trip-transfers are available.

    Returns:
        if OPTIMIZED==1:
            out (list):  list of trips required to cover all optimal journeys Format: [trip_id]
        elif OPTIMIZED==0:
            out (list):  list of routes required to cover all optimal journeys. Format: [route_id]
    '''
    DESTINATION_LIST.remove(SOURCE)
    d_time_list = d_time_groups.get_group(SOURCE)[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist()
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                d_time_list.extend(d_time_groups.get_group(connection[0])[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist())
        except KeyError:
            pass
    d_time_list.sort(key=lambda x: x[1], reverse=True)

    TP_list = []
    J, inf_time = initialize_onemany_tbtr(MAX_TRANSFER, DESTINATION_LIST)
    L = initialize_from_desti_onemany_tbtr(routes_by_stop_dict, stops_dict, DESTINATION_LIST, footpath_dict, idx_by_route_stop_dict)
    R_t = {x: defaultdict(lambda: 1000) for x in range(0, MAX_TRANSFER + 2)}  # assuming maximum route length is 1000

    for dep_details in d_time_list:
        rounds_desti_reached = {x: [] for x in DESTINATION_LIST}
        n = 1
        Q = initialize_from_source_range_tbtr(dep_details, MAX_TRANSFER, stoptimes_dict, R_t)
        dest_list_prime = DESTINATION_LIST.copy()
        while n <= MAX_TRANSFER:
            stop_mark_dict = {stop: 0 for stop in dest_list_prime}
            scope = []
            for counter, trip_segment in enumerate(Q[n]):
                from_stop, tid, to_stop, trip_route, tid_idx = trip_segment[0: 5]
                trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
                connection_list = []
                for desti in dest_list_prime:
                    try:
                        L[desti][trip_route]
                        stop_list, _ = zip(*trip)
                        for last_leg in L[desti][trip_route]:
                            idx = [x[0] for x in enumerate(stop_list) if x[1] == last_leg[2]]
                            if idx and from_stop < last_leg[0] and trip[idx[0]][1] + last_leg[1] < J[desti][n][0]:
                                if last_leg[1] == pd.to_timedelta(0, unit="seconds"):
                                    walking = (0, 0)
                                else:
                                    walking = (1, stops_dict[trip_route][last_leg[0]])
                                J[desti] = update_label_tbtr(trip[idx[0]][1] + last_leg[1], n, (tid, walking, counter), J[desti], MAX_TRANSFER)
                                rounds_desti_reached[desti].append(n)
                    except KeyError:
                        pass
                    try:
                        if tid in trip_set and trip[1][1] < J[desti][n][0]:
                            if stop_mark_dict[desti] == 0:
                                scope.append(desti)
                                stop_mark_dict[desti] = 1
                            connection_list.extend([connection for from_stop_idx, transfer_stop_id in enumerate(trip[1:], from_stop + 1)
                                                    for connection in trip_transfer_dict[tid][from_stop_idx]])
                    except IndexError:
                        pass
                connection_list = list(set(connection_list))
                enqueue_range_tbtr(connection_list, n + 1, (tid, counter, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
            dest_list_prime = [*scope]
            n = n + 1
        for desti in DESTINATION_LIST:
            if rounds_desti_reached[desti]:
                TP_list.extend(
                    post_process_range_onemany_tbtr(J, Q, rounds_desti_reached[desti], PRINT_ITINERARY, desti, SOURCE, footpath_dict, stops_dict, stoptimes_dict,
                                               dep_details[1], MAX_TRANSFER, trip_transfer_dict))
    return TP_list
"""
