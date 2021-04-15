from TBTR.TBTR_functions import *


def TBTR_main(max_transfer, source, destination, d_time, routes_by_stop_dict, stops_dict, stoptimes_dict,
                  footpath_dict, trip_transfer_dict, walking_from_source, print_para, trip_set):
    ################################################################################################################
    J, inf_time = initlize()
    if print_para == 1: print(source, destination, d_time)
    L = initialize_from_desti(routes_by_stop_dict, stops_dict, destination, footpath_dict)

    R_t, Q = initialize_from_source_new(footpath_dict, source, routes_by_stop_dict, stops_dict, stoptimes_dict, d_time,
                                        max_transfer, walking_from_source)

    tau_min = inf_time
    n = 0
    while n < max_transfer:
        for trip in Q[n]:
            from_stop, tid, to_stop, trip_route, tid_idx = trip[0: 5]
            trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
            temp_L = [last_leg for last_leg in L if last_leg[0] == trip_route]
            for last_leg in temp_L:
                stop_list, _ = zip(*trip)
                last_frm_foot_Stop = stops_dict[last_leg[0]][last_leg[1]]
                idx = [x[0] for x in enumerate(stop_list) if x[1] == last_frm_foot_Stop]
                if idx and from_stop < last_leg[1] and trip[idx[0]][1] + last_leg[2] < tau_min:
                    tau_min = trip[idx[0]][1] + last_leg[2]
                    if last_leg[2] == pd.to_timedelta(0, unit="seconds"):
                        walking = (0, 0)
                    else:
                        walking = (1, stops_dict[last_leg[0]][last_leg[1]])
                    J = update_label(tau_min, n, (tid, walking), J)
            if tid in trip_set:
                from_stop_idx_list = [from_stop_idx for from_stop_idx, transfer_stop_id in
                                      enumerate(trip[1:], from_stop + 1) if
                                      transfer_stop_id[1] < tau_min and from_stop_idx in trip_transfer_dict[tid].keys()]
                connection_list = [connection for from_stop_idx in from_stop_idx_list for connection in
                                   trip_transfer_dict[tid][from_stop_idx]]
                enqueue2(connection_list, n + 1, (tid, 0, 0), R_t, Q, stoptimes_dict)
        n = n + 1
    TBTR_out = post_process(J, Q, destination, source, footpath_dict, inf_time, stops_dict, stoptimes_dict, print_para,
                            d_time)
    return TBTR_out
