"""
Module contains rTBTR implementation
"""
from Algorithms.TBTR.TBTR_functions import *


def rtbtr(SOURCE: int, DESTINATION: int, d_time_groups, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int, PRINT_ITINERARY: int, OPTIMIZED: int,
          routes_by_stop_dict: dict, stops_dict: dict, stoptimes_dict: dict, footpath_dict: dict, idx_by_route_stop_dict: dict,
          trip_transfer_dict: dict, trip_set: set) -> list:
    """
    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
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

    Examples:
        >>> output = rtbtr(36, 52, d_time_groups, 4, 1, 1, 0, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict, trip_set)
        >>> print(output)

    See Also:
        One-To-Many rTBTR
    """
    d_time_list = d_time_groups.get_group(SOURCE)[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist()
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                d_time_list.extend(d_time_groups.get_group(connection[0])[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist())
        except KeyError:
            pass
    d_time_list.sort(key=lambda x: x[1], reverse=True)

    out = []
    J = initialize_tbtr(MAX_TRANSFER)
    L = initialize_from_desti(routes_by_stop_dict, stops_dict, DESTINATION, footpath_dict, idx_by_route_stop_dict)
    R_t = {x: defaultdict(lambda: 1000) for x in range(0, MAX_TRANSFER + 2)}

    for dep_details in d_time_list:
        if PRINT_ITINERARY == 1:
            print(f"SOURCE, DESTINATION, d_time: {SOURCE, DESTINATION, dep_details[1]}")
        rounds_desti_reached = []
        Q = initialize_from_source_range(dep_details, MAX_TRANSFER, stoptimes_dict, R_t)
        n = 1
        while n <= MAX_TRANSFER:
            for counter, trip_segment in enumerate(Q[n]):
                from_stop, tid, to_stop, trip_route, tid_idx = trip_segment[0: 5]
                trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
                try:
                    L[trip_route]
                    stop_list, _ = zip(*trip)
                    for last_leg in L[trip_route]:
                        idx = [x[0] for x in enumerate(stop_list) if x[1] == last_leg[2]]
                        if idx and from_stop < last_leg[0] and trip[idx[0]][1] + last_leg[1] < J[n][0]:
                            if last_leg[1] == pd.to_timedelta(0, unit="seconds"):
                                walking = (0, 0)
                            else:
                                walking = (1, stops_dict[trip_route][last_leg[0]])
                            J = update_label(trip[idx[0]][1] + last_leg[1], n, (tid, walking, counter), J, MAX_TRANSFER)
                            rounds_desti_reached.append(n)
                except KeyError:
                    pass
                try:
                    if tid in trip_set and trip[1][1] < J[n][0]:
                        connection_list = [connection for from_stop_idx, transfer_stop_id in enumerate(trip[1:], from_stop + 1)
                                           for connection in trip_transfer_dict[tid][from_stop_idx]]
                        enqueue_range(connection_list, n + 1, (tid, counter, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
                except IndexError:
                    pass
            n = n + 1
        if rounds_desti_reached:
            out.extend(list(post_process_range(J, Q, rounds_desti_reached, PRINT_ITINERARY, DESTINATION,
                                               SOURCE, footpath_dict, stops_dict, stoptimes_dict, dep_details[1],
                                               MAX_TRANSFER, trip_transfer_dict)))
    if OPTIMIZED == 0:
        out = [int(trip.split("_")[0]) for trip in out]
        if PRINT_ITINERARY == 1:
            print('------------------------------------')
    return out
