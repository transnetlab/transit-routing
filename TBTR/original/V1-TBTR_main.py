from TBTR.TBTR_func import *


def TBTR_main(max_transfer, source, destination, d_time, routes_by_stop_dict, stops_dict, stoptimes_dict, footpath_dict, trip_transfer_dict, walking_from_source, print_para):
    ################################################################################################################
    from time import time
    J, inf_time = initlize()
    if print_para==1: print(source, destination, d_time)

    L = initialize_from_desti(routes_by_stop_dict, stops_dict, destination, footpath_dict)

    R_t, Q = initialize_from_source(footpath_dict, source, routes_by_stop_dict, stops_dict, stoptimes_dict, d_time,max_transfer, walking_from_source)

    tau_min = inf_time
    n = 0
    leg_time, second_time = 0, 0
    tot_while=  time()
    while n < max_transfer:
        for trip in Q[n]:
            s = time()
            trip_route = int(trip[2].split("_")[0])
            for last_leg in L:
                if last_leg[0] == trip_route:
                    stop_list, _ = zip(*trip[0])
                    last_frm_foot_Stop = stops_dict[last_leg[0]][last_leg[1]]
                    idx = [x[0] for x in enumerate(stop_list) if x[1]== last_frm_foot_Stop]
                    if idx and trip[1] < last_leg[1] and trip[0][idx[0]][1] + last_leg[2] < tau_min:
                            tau_min = trip[0][idx[0]][1] + last_leg[2]
                            if last_leg[2] == pd.to_timedelta(0, unit="seconds"):
                                walking = (0, 0)
                            else:
                                walking = (1, stops_dict[last_leg[0]][last_leg[1]])
                            J = update_label(tau_min, n, (trip[2], walking), J)
            leg_time = leg_time + time() -s
            second = time()
            try:
                trip_connections = trip_transfer_dict[trip[2]]
                for connection in trip_connections:
                    if trip[1] < connection[0] < trip[3]:
                        if trip[0][connection[0] - trip[1]][1] < tau_min:
                            enqueue(connection[1], connection[2], n + 1, (trip[2], connection), R_t, Q, stoptimes_dict)
            except KeyError:
                pass
            second_time = second_time + time() - second
        n = n + 1
    tot_while = time() - tot_while
    print(leg_time)
    print(tot_while)
    print(second_time)
for x in Q[2]:
    if x[3]!=float('inf') and x[3]!=5:
        break
