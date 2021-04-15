############################################################################################################################################################################################
# Import in the given order!
############################################################################################################################################################################################
from RAPTOR.raptor_functions import *


def rraptor_main(max_transfer, source, destination, d_time_list, routes_by_stop_dict, stops_dict, stoptimes_dict,
                 footpath_dict, print_para, change_time_sec, optimized):
    marked_stop, label, pi_label, star_label, inf_time = initlize(routes_by_stop_dict, source, max_transfer)
    change_time = pd.to_timedelta(change_time_sec, unit='seconds')
    trip_set = []
    route_set = set()
    for d_time in d_time_list:
        pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, max_transfer + 1)}
        marked_stop = deque()
        marked_stop.append(source)
        start_tid, d_time,s_idx = d_time
        ############################################################################################################################################################################################
        # Inputs and check
        ############################################################################################################################################################################################
        #    d_time=pd.to_datetime('2019-10-03 10:33:00')
        #    (source,destination,max_transfer)=(3,9,3)
        if print_para == 1: print(source, destination, d_time)
        # check_stop_validity(stops_file,source,destination)
        ############################################################################################################################################################################################
        # '''Intilization'''
        ############################################################################################################################################################################################
        (label[0][source], star_label[source]) = (d_time, d_time)
        Q = {}

        ######################################################################################################################################################################################################################
        # Main Code
        ######################################################################################################################################################################################################################
        # '''Main code part 1'''
        for k in range(1, max_transfer + 1):
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
            ############################################################################################################################################################################################################################################
            # '''Main code part 2'''
            for route, current_stopindex_by_route in Q.items():
                current_trip_t = -1
                for p_i in stops_dict[route][current_stopindex_by_route:]:
                    if current_trip_t != -1 and current_trip_t[current_stopindex_by_route][1] < min(star_label[p_i],star_label[destination]):
                        arr_by_t_at_pi = current_trip_t[current_stopindex_by_route][1]
                        label[k][p_i], star_label[p_i] = arr_by_t_at_pi, arr_by_t_at_pi
                        pi_label[k][p_i] = (boarding_time, borading_point, p_i, arr_by_t_at_pi, tid)
                        marked_stop.append(p_i)
                    if current_trip_t == -1 or label[k - 1][p_i] + change_time < current_trip_t[current_stopindex_by_route][1]:
                        tid, current_trip_t = get_latest_trip_new(stoptimes_dict, route, label[k - 1][p_i],current_stopindex_by_route, change_time)
                        if current_trip_t == -1:
                            boarding_time, borading_point = -1, -1
                        else:
                            borading_point = p_i
                            boarding_time = current_trip_t[current_stopindex_by_route][1]
                    current_stopindex_by_route = current_stopindex_by_route + 1
            #######################################################################################################################################################################################################################################################################
            # '''Main code part 3'''
            marked_stop_copy = [*marked_stop]
            for p in marked_stop_copy:
                try:
                    trans_info = footpath_dict[p]
                    for i in trans_info:
                        (p_dash, to_pdash_time) = i
                        new_p_dash_time = label[k][p] + to_pdash_time
                        if (label[k][p_dash] > new_p_dash_time) and new_p_dash_time < min(star_label[p_dash], star_label[destination]):
                            label[k][p_dash], star_label[p_dash] = new_p_dash_time, new_p_dash_time
                            pi_label[k][p_dash] = ('walking', p, p_dash, to_pdash_time, new_p_dash_time)
                            marked_stop.append(p_dash)
                except KeyError:
                    continue
            ###########################################################################################################################################################################################################################################################################
            # '''Main code End'''
            if marked_stop == deque([]):
                #            print('code ended with termination condition')
                break
        #############################################################################################################################################################################################################################################################################
        if optimized == 1:
            trip_set.extend(post_processing_rraptor_partial(destination, pi_label))
        else:
            route_set = post_processing_rraptor_full(destination, pi_label, print_para, label, route_set)
        if print_para == 1: print('------------------------------------')
    if optimized == 1:
        return trip_set
    else:
        return route_set