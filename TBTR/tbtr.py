"""
Module contains TBTR implementation
#TODO: Add backtracking label system
"""
from TBTR.TBTR_functions import *


def tbtr(SOURCE, DESTINATION, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE, PRINT_PARA, routes_by_stop_dict, stops_dict,
         stoptimes_dict, footpath_dict, trip_transfer_dict, trip_set):
    """
    Standard TBTR implementation.
    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        MAX_TRANSFER (int): maximum transfer limit.
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        PRINT_PARA (int): 1 or 0. 1 means print complete path.
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples
        of form (id of trip we are transferring to, stop number)}
        trip_set (set): set of trip ids from which trip-transfers are available.
    Returns:
        out (list): List of pareto-optimal arrival Timestamps
    """
    out = []
    J = initialize_tbtr()
    L = initialize_from_desti_new(routes_by_stop_dict, stops_dict, DESTINATION, footpath_dict)
    R_t, Q = initialize_from_source_new(footpath_dict, SOURCE, routes_by_stop_dict, stops_dict, stoptimes_dict, D_TIME,
                                        MAX_TRANSFER, WALKING_FROM_SOURCE)
    n = 0
    while n < MAX_TRANSFER:  # TODO: Pseudocdoe is n \leq \lambda?
        for trip in Q[n]:
            from_stop, tid, to_stop, trip_route, tid_idx = trip[0: 5]  # TODO: can you use a different name in 36 and 37 instead of trip so that it is not confused with 38
            trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
            try:
                L[trip_route]  # TODO: what's this line doing? Checking if trip_route is in L?
                stop_list, _ = zip(*trip)
                for last_leg in L[trip_route]:
                    idx = [x[0] for x in enumerate(stop_list) if x[1] == last_leg[2]]
                    if idx and from_stop < last_leg[0] and trip[idx[0]][1] + last_leg[1] < J[n][0]:
                        if last_leg[1] == 0:
                            walking = (0, 0)  # TODO: Is this for tracking the path? I don't see it in the pseudocode
                        else:
                            walking = (1, stops_dict[trip_route][last_leg[0]])
                        J = update_label(trip[idx[0]][1] + last_leg[1], n, (tid, walking), J, MAX_TRANSFER)
            except KeyError:
                pass
            try:
                if tid in trip_set and trip[1][1] < J[n][0]:
                    connection_list = [connection for from_stop_idx, transfer_stop_id in
                                       enumerate(trip[1:], from_stop + 1)
                                       for connection in trip_transfer_dict[tid][from_stop_idx]]
                    enqueue(connection_list, n + 1, (tid, 0, 0), R_t, Q, stoptimes_dict)
            except IndexError:
                pass
        n = n + 1
    TBTR_out = post_process(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, PRINT_PARA, D_TIME,
                            MAX_TRANSFER)
    out.append(TBTR_out)
    return out
