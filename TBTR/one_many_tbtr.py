"""
Module contains One-To-Many rTBTR implementation
#TODO: Add backtracking label
"""
from TBTR.TBTR_functions import *


def onetomany_rtbtr(SOURCE, DESTINATION_LIST, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA, OPTIMIZED,
                    routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, trip_transfer_dict, trip_set):
    """
    One to many rTBTR implementation
    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION_LIST (list): list of stop ids of destination stop.
        d_time_groups (pandas.group): all possible departures times from all stops.
        MAX_TRANSFER (int): maximum transfer limit.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        PRINT_PARA (int): 1 or 0. 1 means print complete path.
        OPTIMIZED (int): 1 or 0. 1 means collect trips and 0 means collect routes.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {keys: stop number, value: list of tuples of form (id of trip we are transferring to, stop number)}.
        trip_set (set): set of trip ids from which trip-transfers are available.
    Returns:
        if OPTIMIZED==1:
            out (list):  list of trips required to cover all optimal journeys Format: [trip_id]
        elif OPTIMIZED==0:
            out (list):  list of routes required to cover all optimal journeys. Format: [route_id]
    """
    d_time_list = d_time_groups.get_group(SOURCE)[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist()
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                d_time_list.extend(d_time_groups.get_group(connection[0])[
                                       ["trip_id", 'arrival_time', 'stop_sequence']].values.tolist())
        except KeyError:
            pass
    d_time_list.sort(key=lambda x: x[1], reverse=True)

    out = []
    J, inf_time = initialize_onemany(MAX_TRANSFER, DESTINATION_LIST)
    L = initialize_from_desti_onemany(routes_by_stop_dict, stops_dict, DESTINATION_LIST, footpath_dict)
    R_t = {x: defaultdict(lambda: 1000) for x in range(0, MAX_TRANSFER + 1)}

    for d_time in d_time_list:
        rounds_desti_reached = {x: [] for x in DESTINATION_LIST}
        n = 0
        Q = initialize_from_source_range(d_time, MAX_TRANSFER, stoptimes_dict, n, R_t)
        while n < MAX_TRANSFER:
            for trip in Q[n]:
                from_stop, tid, to_stop, trip_route, tid_idx = trip[0: 5]
                trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
                connection_list = []
                for desti in DESTINATION_LIST:
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
                                J[desti] = update_label(trip[idx[0]][1] + last_leg[1], n, (tid, walking), J[desti],
                                                        MAX_TRANSFER)
                                rounds_desti_reached[desti].append(n)
                    except KeyError:
                        pass
                    try:
                        if tid in trip_set and trip[1][1] < J[desti][n][0]:
                            connection_list.extend(
                                [connection for from_stop_idx, transfer_stop_id in enumerate(trip[1:], from_stop + 1)
                                 for connection in trip_transfer_dict[tid][from_stop_idx]])
                    except IndexError:
                        pass
                enqueue_range2(connection_list, n + 1, (tid, 0, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
            n = n + 1
        for desti in DESTINATION_LIST:
            if rounds_desti_reached[desti]:
                out.extend(post_process_range_onemany(J, Q, rounds_desti_reached[desti], desti))
    if OPTIMIZED == 1:
        out = [int(trip.split("_")[0]) for trip in out]
    return list(set(out))
