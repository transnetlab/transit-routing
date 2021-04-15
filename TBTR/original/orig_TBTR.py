from TBTR.TBTR_func import *


def TBTR_main(max_transfer, source, destination, d_time, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict,
              transfers_file, trip_transfer_dict, walking_from_source, print_para):
    ################################################################################################################
    J, inf_time = initlize()
    if print_para==1: print(source, destination, d_time)

    L = initialize_from_desti(routes_by_stop_dict, stops_dict, destination, footpath_dict)

    R_t, Q = initialize_from_source(footpath_dict, source, routes_by_stop_dict, stops_dict, stoptimes_dict, d_time,max_transfer, walking_from_source)

    tau_min = inf_time
    n = 0
    while n < max_transfer:
        for trip in Q[n]:
            breakdown = [int(x) for x in trip[2].split("_")]
            for last_leg in L:
                try:
                    stop_list, _ = zip(*trip[0])
                    idx = stop_list.index(stops_dict[last_leg[0]][last_leg[1]])
                    if trip[1] < last_leg[1] and trip[0][idx][1] + last_leg[2] < tau_min:
                        tau_min = trip[0][idx][1] + last_leg[2]
                        if last_leg[2] == pd.to_timedelta(0, unit="seconds"):
                            walking = (0, 0)
                        else:
                            walking = (1, stops_dict[last_leg[0]][last_leg[1]])
                        J = update_label(tau_min, n, (trip[2], walking), J)
                except ValueError:
                    pass
            try:
                trip_connections = trip_transfer_dict[trip[2]]
                for connection in trip_connections:
                    if trip[1] < connection[0] < trip[3]:
                        if trip[0][connection[0] - trip[1]][1] < tau_min:
                            enqueue(connection[1], connection[2], n + 1, (trip[2], connection), R_t, Q, stoptimes_dict)
            except KeyError:
                pass
        n = n + 1
    TBTR_out = post_process(J, Q, destination, source, footpath_dict, inf_time, stops_dict, stoptimes_dict, print_para,d_time)
    return TBTR_out
