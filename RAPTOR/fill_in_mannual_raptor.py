############################################################################################################################################################################################
# Import in the given order!
############################################################################################################################################################################################
import numpy as np

from RAPTOR.raptor_functions import *


def fill_in_rap(max_transfer, source, destination, d_time, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, walking_from_source, print_para, save_routes, change_time_sec):
    start_tid, d_time = d_time
    routes_exp = {}
    ############################################################################################################################################################################################
    # Inputs and check
    ############################################################################################################################################################################################
    #    d_time=pd.to_datetime('2019-10-03 06:00:00')
    #    (source,destination,max_transfer)=(3,9,3)
    if print_para==1:print(source,destination,d_time)
    # check_stop_validity(stops_file,source,destination)
    ############################################################################################################################################################################################
    # '''Intilization'''
    ############################################################################################################################################################################################
    marked_stop, label, pi_label, star_label, inf_time = initlize(routes_by_stop_dict, source, max_transfer)
    change_time = pd.to_timedelta(change_time_sec,unit='seconds')
    (label[0][source], star_label[source]) = (d_time, d_time)
    Q = {}
    if walking_from_source == 1:
        try:
            trans_info = footpath_dict[source]
            for i in trans_info:
                (p_dash, to_pdash_time) = i
                label[0][p_dash] = d_time + to_pdash_time
                star_label[p_dash] = d_time + to_pdash_time
                pi_label[0][p_dash] = ('walking', source, p_dash, to_pdash_time, d_time + to_pdash_time)
                marked_stop.append(p_dash)
        except KeyError:
            pass

    ######################################################################################################################################################################################################################
    # Main Code
    ######################################################################################################################################################################################################################
    # '''Main code part 1'''
    for k in range(1, max_transfer + 1):
        Q.clear()  # Format of Q is {route:stop}
        while marked_stop:
            p = marked_stop.pop()
            if k == 1:
                Q[int(start_tid.split('_')[0])] = source
                break
            try:
                routes_serving_p = routes_by_stop_dict[p]
            except KeyError:
                continue
            for route in routes_serving_p:
                if route in Q.keys() and Q[route] != p:
                    Q[route] = stops_dict[route][min(stops_dict[route].index(Q[route]), stops_dict[route].index(p))]
                else:
                    Q[route] = p
        ############################################################################################################################################################################################################################################
        # '''Main code part 2'''
        routes_exp[k] = list(Q.keys())
        for route in Q.keys():
            start_stopindex_by_route = stops_dict[route].index(Q[route])
            current_stopindex_by_route = start_stopindex_by_route
            current_trip_t = -1
            arr_by_t_at_pi = inf_time  # dep and arr is assumed same. else change here
            for p_i in stops_dict[route][start_stopindex_by_route:]:
                previous_arrival_at_pi = label[k - 1][p_i]
                if current_trip_t != -1:
                    arr_by_t_at_pi = arri_by_t_at_pi(current_trip_t, p_i)
                    if arr_by_t_at_pi < min(star_label[p_i], star_label[destination]):
                        label[k][p_i], star_label[p_i] = arr_by_t_at_pi, arr_by_t_at_pi
                        pi_label[k][p_i] = (boarding_time, borading_point, p_i, arr_by_t_at_pi, tid)
                        marked_stop.append(p_i)
                #                        if p_i == destination: print(k, route, label[k][destination])
                #                        if p_i == destination and route == 20070: print(label[k][destination])
                if current_trip_t != -1 and p_i_is_last_stop_for_currentTrip(current_trip_t, p_i):
                    break
                if current_trip_t == -1 or previous_arrival_at_pi + change_time < arri_by_t_at_pi(current_trip_t,p_i):
                    tid, current_trip_t = get_latest_trip_new(stoptimes_dict, route, p_i, previous_arrival_at_pi, current_stopindex_by_route, change_time)
                    if current_trip_t == -1:
                        boarding_time: np.NaN
                        borading_point = -1
                    else:
                        borading_point = p_i
                        boarding_time = arri_by_t_at_pi(current_trip_t, borading_point)
                current_stopindex_by_route = current_stopindex_by_route + 1
        #######################################################################################################################################################################################################################################################################
        # '''Main code part 3'''
        marked_stop_copy = [*marked_stop]
        for p in marked_stop_copy:
            try:
                trans_info = footpath_dict[p]
                for i in trans_info:
                    (p_dash, to_pdash_time) = i
                    if (label[k][p_dash] > label[k][p] + to_pdash_time) and (label[k][p] + to_pdash_time) < min(
                            star_label[p_dash], star_label[destination]):
                        label[k][p_dash] = label[k][p] + to_pdash_time
                        star_label[p_dash] = label[k][p] + to_pdash_time
                        pi_label[k][p_dash] = ('walking', p, p_dash, to_pdash_time, label[k][p_dash])
                        marked_stop.append(p_dash)
            except KeyError:
                continue
        ###########################################################################################################################################################################################################################################################################
        # '''Main code End'''
        if marked_stop == deque([]):
            #            print('code ended with termination condition')
            break
    #############################################################################################################################################################################################################################################################################

    _ , _, rap_out = post_processing(destination, pi_label,print_para, label, save_routes, routes_exp)
    if print_para == 1: print('------------------------------------')
