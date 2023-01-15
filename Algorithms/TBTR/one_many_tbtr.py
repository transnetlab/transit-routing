"""
Module contains One-To-Many rTBTR implementation
"""
from Algorithms.TBTR.TBTR_functions import *


def onetomany_rtbtr(SOURCE: int, DESTINATION_LIST: list, d_time_groups, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int,
                    PRINT_ITINERARY: int, OPTIMIZED: int, routes_by_stop_dict: dict, stops_dict: dict, stoptimes_dict: dict,
                    footpath_dict: dict, idx_by_route_stop_dict: dict, trip_transfer_dict: dict, trip_set: set) -> list:
    """
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

    Examples:
        >>> output = onetomany_rtbtr(36, [52, 43], d_time_groups, 4, 1, 1, 0, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, idx_by_route_stop_dict, trip_transfer_dict, trip_set)
        >>> print(output)

    See Also:
        HypTBTR, One-To-Many rRAPTOR
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
    J, inf_time = initialize_onemany(MAX_TRANSFER, DESTINATION_LIST)
    L = initialize_from_desti_onemany(routes_by_stop_dict, stops_dict, DESTINATION_LIST, footpath_dict, idx_by_route_stop_dict)
    R_t = {x: defaultdict(lambda: 1000) for x in range(0, MAX_TRANSFER + 2)}  # assuming maximum route length is 1000

    for dep_details in d_time_list:
        rounds_desti_reached = {x: [] for x in DESTINATION_LIST}
        n = 1
        Q = initialize_from_source_range(dep_details, MAX_TRANSFER, stoptimes_dict, R_t)
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
                                J[desti] = update_label(trip[idx[0]][1] + last_leg[1], n, (tid, walking, counter), J[desti], MAX_TRANSFER)
                                rounds_desti_reached[desti].append(n)
                    except KeyError:
                        pass
                    try:
                        if tid in trip_set and trip[1][1] < J[desti][n][0]:
                            if stop_mark_dict[desti]==0:
                                scope.append(desti)
                                stop_mark_dict[desti]=1
                            connection_list.extend([connection for from_stop_idx, transfer_stop_id in enumerate(trip[1:], from_stop + 1)
                                 for connection in trip_transfer_dict[tid][from_stop_idx]])
                    except IndexError:
                        pass
                connection_list = list(set(connection_list))
                enqueue_range(connection_list, n + 1, (tid, counter, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
            dest_list_prime = [*scope]
            n = n + 1
        for desti in DESTINATION_LIST:
            if rounds_desti_reached[desti]:
                out.extend(post_process_range_onemany(J, Q, rounds_desti_reached[desti], PRINT_ITINERARY, desti, SOURCE, footpath_dict, stops_dict, stoptimes_dict, dep_details[1], MAX_TRANSFER, trip_transfer_dict))
    if OPTIMIZED == 0:
        out = [int(trip.split("_")[0]) for trip in out]
    return out
