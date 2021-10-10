############################################################################################################################################################################################
# Import in the given order!
############################################################################################################################################################################################
from RAPTOR.raptor_functions import *


def rraptor(SOURCE, DESTINATION, d_time_groups, MAX_TRANSFER, WALKING_FROM_SOURCE, CHANGE_TIME_SEC, PRINT_PARA, OPTIMIZED,
                 routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict):
    '''
    Standard Raptor implementation
    Args:
        SOURCE (int): stop-id DESTINATION stop
        DESTINATION (int): stop-id SOURCE stop
        d_time_groups (pandas.group):
        MAX_TRANSFER (int): Max transfer limit
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        CHANGE_TIME_SEC (int): Change time in seconds
        PRINT_PARA (int): 1 or 0. 1 means print complete path
        optimized (int): 1 or 0. 1 means collect trips and 0 means collect routes
        routes_by_stop_dict (dict): Pre-processed dict- format {stop_id: [routes]}
        stops_dict (dict): Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict (dict): Pre-processed dict- format {route_id: [[trip_1], [trip_2]]}
        footpath_dict (dict): Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}
    Returns:
        if optimized==1:
            out (list):  List of trips required to cover all optimal journeys Format: [trip_id]
        else:
            out (list):  List of routes required to cover all optimal journeys. Format: [route_id]
    '''
    out = []

    d_time_list = d_time_groups.get_group(SOURCE)[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist()
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                d_time_list.extend(d_time_groups.get_group(connection[0])[["trip_id", 'arrival_time', 'stop_sequence']].values.tolist())
        except KeyError:
            pass
    d_time_list.sort(key=lambda x: x[1], reverse=True)


    marked_stop, label, pi_label, star_label, inf_time = initlize_raptor(routes_by_stop_dict, SOURCE, MAX_TRANSFER)
    change_time = pd.to_timedelta(CHANGE_TIME_SEC, unit='seconds')

    for d_time in d_time_list:
        pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, MAX_TRANSFER + 1)}
        marked_stop = deque()
        marked_stop.append(SOURCE)
        start_tid, d_time, s_idx = d_time
        if PRINT_PARA == 1: print(f"SOURCE, DESTINATION, d_time: {SOURCE, DESTINATION, d_time}")
        # '''Intilization'''
        (label[0][SOURCE], star_label[SOURCE]) = (d_time, d_time)
        Q = {}
        # Main Code
        # '''Main code part 1'''
        for k in range(1, MAX_TRANSFER + 1):
            Q.clear()  # Format of Q is {route:stop}
            marked_stop = list(set(marked_stop))
            while marked_stop:
                p = marked_stop.pop()
                if k == 1:
                    Q[int(start_tid.split('_')[0])] = s_idx
                    break
                try:
                    routes_serving_p = routes_by_stop_dict[p]
                    for route in routes_serving_p:
                        stp_idx = stops_dict[route].index(p)
                        if route in Q.keys() and Q[route] != stp_idx:
                            Q[route] = min(stp_idx, Q[route])
                        else:
                            Q[route] = stp_idx
                except KeyError:
                    continue
            # '''Main code part 2'''
            for route, current_stopindex_by_route in Q.items():
                current_trip_t = -1
                for p_i in stops_dict[route][current_stopindex_by_route:]:
                    if current_trip_t != -1 and current_trip_t[current_stopindex_by_route][1] < min(star_label[p_i],
                                                                                                    star_label[
                                                                                                        DESTINATION]):
                        arr_by_t_at_pi = current_trip_t[current_stopindex_by_route][1]
                        label[k][p_i], star_label[p_i] = arr_by_t_at_pi, arr_by_t_at_pi
                        pi_label[k][p_i] = (boarding_time, borading_point, p_i, arr_by_t_at_pi, tid)
                        marked_stop.append(p_i)
                    if current_trip_t == -1 or label[k - 1][p_i] + change_time < \
                            current_trip_t[current_stopindex_by_route][1]:
                        tid, current_trip_t = get_latest_trip_new(stoptimes_dict, route, label[k - 1][p_i],
                                                                  current_stopindex_by_route, change_time)
                        if current_trip_t == -1:
                            boarding_time, borading_point = -1, -1
                        else:
                            borading_point = p_i
                            boarding_time = current_trip_t[current_stopindex_by_route][1]
                    current_stopindex_by_route = current_stopindex_by_route + 1
            # '''Main code part 3'''
            marked_stop_copy = [*marked_stop]
            for p in marked_stop_copy:
                try:
                    trans_info = footpath_dict[p]
                    for i in trans_info:
                        (p_dash, to_pdash_time) = i
                        new_p_dash_time = label[k][p] + to_pdash_time
                        if (label[k][p_dash] > new_p_dash_time) and new_p_dash_time < min(star_label[p_dash],
                                                                                          star_label[DESTINATION]):
                            label[k][p_dash], star_label[p_dash] = new_p_dash_time, new_p_dash_time
                            pi_label[k][p_dash] = ('walking', p, p_dash, to_pdash_time, new_p_dash_time)
                            marked_stop.append(p_dash)
                except KeyError:
                    continue
            # '''Main code End'''
            if marked_stop == deque([]):
                #print('code ended with termination condition')
                break
        out.extend(post_processing_rraptor(DESTINATION, pi_label, PRINT_PARA, label, OPTIMIZED))
        if PRINT_PARA == 1: print('------------------------------------')
    return list(set(out))

