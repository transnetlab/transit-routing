############################################################################################################################################################################################
# Import in the given order!
############################################################################################################################################################################################
import numpy as np

from RAPTOR.raptor_functions import *


def fill_in_rap(MAX_TRANSFER, SOURCE, DESTINATION, D_TIME, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, WALKING_FROM_SOURCE, PRINT_PARA, save_routes, CHANGE_TIME_SEC):
    start_tid, D_TIME = D_TIME
    routes_exp = {}
    ############################################################################################################################################################################################
    # Inputs and check
    ############################################################################################################################################################################################
    #    D_TIME=pd.to_datetime('2019-10-03 06:00:00')
    #    (SOURCE,DESTINATION,MAX_TRANSFER)=(3,9,3)
    if PRINT_PARA==1:print(SOURCE,DESTINATION,D_TIME)
    # check_stop_validity(stops_file,SOURCE,DESTINATION)
    ############################################################################################################################################################################################
    # '''Intilization'''
    ############################################################################################################################################################################################
    marked_stop, label, pi_label, star_label, inf_time = initlize(routes_by_stop_dict, SOURCE, MAX_TRANSFER)
    change_time = pd.to_timedelta(CHANGE_TIME_SEC,unit='seconds')
    (label[0][SOURCE], star_label[SOURCE]) = (D_TIME, D_TIME)
    Q = {}
    if WALKING_FROM_SOURCE == 1:
        try:
            trans_info = footpath_dict[SOURCE]
            for i in trans_info:
                (p_dash, to_pdash_time) = i
                label[0][p_dash] = D_TIME + to_pdash_time
                star_label[p_dash] = D_TIME + to_pdash_time
                pi_label[0][p_dash] = ('walking', SOURCE, p_dash, to_pdash_time, D_TIME + to_pdash_time)
                marked_stop.append(p_dash)
        except KeyError:
            pass

    ######################################################################################################################################################################################################################
    # Main Code
    ######################################################################################################################################################################################################################
    # '''Main code part 1'''
    for k in range(1, MAX_TRANSFER + 1):
        Q.clear()  # Format of Q is {route:stop}
        while marked_stop:
            p = marked_stop.pop()
            if k == 1:
                Q[int(start_tid.split('_')[0])] = SOURCE
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
                    if arr_by_t_at_pi < min(star_label[p_i], star_label[DESTINATION]):
                        label[k][p_i], star_label[p_i] = arr_by_t_at_pi, arr_by_t_at_pi
                        pi_label[k][p_i] = (boarding_time, borading_point, p_i, arr_by_t_at_pi, tid)
                        marked_stop.append(p_i)
                #                        if p_i == DESTINATION: print(k, route, label[k][DESTINATION])
                #                        if p_i == DESTINATION and route == 20070: print(label[k][DESTINATION])
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
                            star_label[p_dash], star_label[DESTINATION]):
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

    _ , _, rap_out = post_processing(DESTINATION, pi_label,PRINT_PARA, label, save_routes, routes_exp)
    if PRINT_PARA == 1: print('------------------------------------')
