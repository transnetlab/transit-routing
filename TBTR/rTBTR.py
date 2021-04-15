from TBTR.TBTR_functions import *


def range_TBTR_main(max_transfer, source, destination, d_time_list, routes_by_stop_dict, stops_dict, stoptimes_dict,
                    footpath_dict, trip_transfer_dict, trip_set):
    ################################################################################################################
    final_out_trips = set()
    J, inf_time = initlize()

    L = initialize_from_desti(routes_by_stop_dict, stops_dict, destination, footpath_dict)

    R_t = {x: defaultdict(lambda: 1000) for x in range(0, max_transfer + 1)}

    for d_time in d_time_list:
        rounds_desti_reached = []
        n = 0
        Q = initialize_from_source_range(d_time, max_transfer, stops_dict, stoptimes_dict, source, n, R_t)
        while n < max_transfer:
            for trip in Q[n]:
                from_stop, tid, to_stop, trip_route, tid_idx = trip[0: 5]
                trip = stoptimes_dict[trip_route][tid_idx][from_stop:to_stop]
                temp_L = [last_leg for last_leg in L if last_leg[0] == trip_route]
                for last_leg in temp_L:
                    stop_list, _ = zip(*trip)
                    last_frm_foot_Stop = stops_dict[last_leg[0]][last_leg[1]]
                    idx = [x[0] for x in enumerate(stop_list) if x[1] == last_frm_foot_Stop]
                    if idx and from_stop < last_leg[1] and trip[idx[0]][1] + last_leg[2] < J[n][0]:
                        if last_leg[2] == pd.to_timedelta(0, unit="seconds"):
                            walking = (0, 0)
                        else:
                            walking = (1, stops_dict[last_leg[0]][last_leg[1]])
                        J = update_label(trip[idx[0]][1] + last_leg[2], n, (tid, walking), J)
                        rounds_desti_reached.append(n)
                if tid in trip_set:
                    from_stop_idx_list = [from_stop_idx for from_stop_idx, transfer_stop_id in
                                          enumerate(trip[1:], from_stop + 1) if
                                          transfer_stop_id[1] < J[n][0] and from_stop_idx in trip_transfer_dict[tid].keys()]
                    connection_list = [connection for from_stop_idx in from_stop_idx_list for connection in
                                       trip_transfer_dict[tid][from_stop_idx]]
                    enqueue_range2(connection_list, n + 1, (tid, 0, 0), R_t, Q, stoptimes_dict, max_transfer)
            n = n + 1
        if rounds_desti_reached:
            TBTR_out = post_process_range(J, Q, rounds_desti_reached)
            final_out_trips = final_out_trips.union(TBTR_out)
    return final_out_trips