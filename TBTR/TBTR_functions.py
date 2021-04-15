from collections import defaultdict
from collections import deque

import pandas as pd


def initlize():
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    J = defaultdict(lambda: [inf_time, 0])
    return J, inf_time


def initialize_from_desti(routes_by_stop_dict, stops_dict, destination, footpath_dict):
    L = []
    try:
        transfer_to_desti = footpath_dict[destination]
        for from_stop, foot_time in transfer_to_desti:
            try:
                walkalble_desti_route = routes_by_stop_dict[from_stop]
                for route in walkalble_desti_route:
                    L.append((route, stops_dict[route].index(from_stop), foot_time))
            except KeyError:
                pass  # Line 1 Curtailed network and full transfer file will cause error.
    except KeyError:
        pass
    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[destination]:
        L.append((route, stops_dict[route].index(destination), delta_tau))
    return L


def initialize_from_desti_old(transfers_file, routes_by_stop_dict, stops_dict, destination):
    L = []
    transfer_to_desti = transfers_file[transfers_file.to_stop_id == destination][['from_stop_id', 'min_transfer_time']]
    for _, row in transfer_to_desti.iterrows():
        delta_tau = pd.to_timedelta(row.min_transfer_time, unit="seconds")
        try:
            walkalble_desti_route = routes_by_stop_dict[row.from_stop_id]
            for route in walkalble_desti_route:
                L.append((route, stops_dict[route].index(row.from_stop_id), delta_tau))
        except KeyError:
            pass  # Line 1 Curtailed network and full transfer file will cause error.
    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[destination]:
        L.append((route, stops_dict[route].index(destination), delta_tau))
    return L


def initialize_from_source_range(d_time, max_transfer, stops_dict, stoptimes_dict, source, n, R_t):
    Q = [[] for x in range(max_transfer + 1)]
    route, trip_idx = [int(x) for x in d_time[0].split("_")]
    stop_index = d_time[2]
    enqueue_range1(f'{route}_{trip_idx}', stop_index, n, (0, 0), R_t, Q, stoptimes_dict, max_transfer)
    return Q

def enqueue_range1(to_trip_id, to_trip_id_stop, n, pointer, R_t, Q, stoptimes_dict, max_transfer):
    if to_trip_id_stop < R_t[n][to_trip_id]:
        route, tid = [int(x) for x in to_trip_id.split("_")]
        Q[n].append((to_trip_id_stop, to_trip_id, R_t[n][to_trip_id], route, tid, pointer))
        for x in range(tid, len(stoptimes_dict[route]) + 1):
            for r in range(n, max_transfer+ 1):
                R_t[r][f"{route}_{x}"] = min(R_t[r][f"{route}_{x}"], to_trip_id_stop)

def enqueue_range2(connection_list, nextround, pointer, R_t, Q, stoptimes_dict, max_transfer):
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[nextround][to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[nextround].append((to_trip_id_stop, to_trip_id, R_t[nextround][to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                for r in range(nextround, max_transfer+ 1):
                    R_t[r][f"{route}_{x}"] = min(R_t[r][f"{route}_{x}"], to_trip_id_stop)

def initialize_from_source_new(footpath_dict, source, routes_by_stop_dict, stops_dict, stoptimes_dict, d_time,
                               max_transfer, walking_from_source):
    Q = [[] for x in range(max_transfer + 1)]
    R_t = defaultdict(lambda: 1000)
    if walking_from_source == 1:
        try:
            source_footpaths = footpath_dict[source]
            for connection in source_footpaths:
                delta_tau = connection[1]
                walkable_source_routes = routes_by_stop_dict[connection[0]]
                for route in walkable_source_routes:
                    stop_index = stops_dict[route].index(connection[0])
                    route_trip = stoptimes_dict[route]
                    for trip_idx, trip in enumerate(route_trip):
                        if d_time + delta_tau <= trip[stop_index][1]:
                            enqueue1(f'{route}_{trip_idx}', stop_index, 0, (0, connection[0]), R_t, Q,
                                        stoptimes_dict)
                            break
        except KeyError:
            pass
    #    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[source]:
        stop_index = stops_dict[route].index(source)
        route_trip = stoptimes_dict[route]
        for trip_idx, trip in enumerate(route_trip):
            #            if d_time + delta_tau <= trip[stop_index][1]:
            if d_time <= trip[stop_index][1]:
                enqueue1(f'{route}_{trip_idx}', stop_index, 0, (0, 0), R_t, Q, stoptimes_dict)
                break
    return R_t, Q


def initialize_from_source(footpath_dict, source, routes_by_stop_dict, stops_dict, stoptimes_dict, d_time, max_transfer,
                           walking_from_source):
    Q = [deque() for x in range(max_transfer + 1)]
    R_t = defaultdict(lambda: 1000)
    if walking_from_source == 1:
        try:
            source_footpaths = footpath_dict[source]
            for connection in source_footpaths:
                delta_tau = connection[1]
                walkable_source_routes = routes_by_stop_dict[connection[0]]
                for route in walkable_source_routes:
                    stop_index = stops_dict[route].index(connection[0])
                    route_trip = stoptimes_dict[route]
                    for trip_idx, trip in enumerate(route_trip):
                        if d_time + delta_tau <= trip[stop_index][1]:
                            enqueue(f'{route}_{trip_idx}', stop_index, 0, (0, connection[0]), R_t, Q, stoptimes_dict)
                            break
        except KeyError:
            pass
    #    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[source]:
        stop_index = stops_dict[route].index(source)
        route_trip = stoptimes_dict[route]
        for trip_idx, trip in enumerate(route_trip):
            #            if d_time + delta_tau <= trip[stop_index][1]:
            if d_time <= trip[stop_index][1]:
                enqueue(f'{route}_{trip_idx}', stop_index, 0, (0, 0), R_t, Q, stoptimes_dict)
                break
    return R_t, Q


def enqueue2(connection_list, round, pointer, R_t, Q, stoptimes_dict):
    """
    :param 2ztrip_inde: trip Id to be added to the queue
    :param stop_index: stop from which above trip Id is to be added
    :param transfer_count: Round into which it is to be added
    :param pointer: (a,b) a - from trip Id, (stop of from trip id, to trip Id, to trip_id stop)
    """
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                R_t[f"{route}_{x}"] = min(R_t[f"{route}_{x}"], to_trip_id_stop)


def enqueue1(to_trip_id, to_trip_id_stop, round, pointer, R_t, Q, stoptimes_dict):
    """
    :param 2ztrip_inde: trip Id to be added to the queue
    :param stop_index: stop from which above trip Id is to be added
    :param transfer_count: Round into which it is to be added
    :param pointer: (a,b) a - from trip Id, (stop of from trip id, to trip Id, to trip_id stop)
    """
    if to_trip_id_stop < R_t[to_trip_id]:
        route, tid = [int(x) for x in to_trip_id.split("_")]
        Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
        for x in range(tid, len(stoptimes_dict[route]) + 1):
            R_t[f"{route}_{x}"] = min(R_t[f"{route}_{x}"], to_trip_id_stop)

def enqueue(to_trip_id, to_trip_id_stop, round, pointer, R_t, Q, stoptimes_dict):
    """
    :param 2ztrip_inde: trip Id to be added to the queue
    :param stop_index: stop from which above trip Id is to be added
    :param transfer_count: Round into which it is to be added
    :param pointer: (a,b) a - from trip Id, (stop of from trip id, to trip Id, to trip_id stop)
    """
    if to_trip_id_stop < R_t[to_trip_id]:
        break_down = [int(x) for x in to_trip_id.split("_")]
        if R_t[to_trip_id] == 1000:
            Q[round].append((
                            stoptimes_dict[break_down[0]][break_down[1]][to_trip_id_stop:], to_trip_id_stop, to_trip_id,
                            R_t[to_trip_id], pointer))
        else:
            Q[round].append((stoptimes_dict[break_down[0]][break_down[1]][to_trip_id_stop:R_t[to_trip_id]],
                             to_trip_id_stop, to_trip_id, R_t[to_trip_id], pointer))
        for x in range(break_down[1], len(stoptimes_dict[break_down[0]]) + 1):
            R_t[f"{break_down[0]}_{x}"] = min(R_t[f"{break_down[0]}_{x}"], to_trip_id_stop)


def update_label(label, round, trip_id, J):
    if J[round][0] > label:
        J[round][0] = label
        J[round][1] = trip_id
    return J

def post_process_range(J, Q, rounds_desti_reached):
    rounds_desti_reached = list(set(rounds_desti_reached))
    TBTR_out = []
    for x in reversed(rounds_desti_reached):
        round = x
        current_trip = J[x][1][0]
        journey = []
        while current_trip!=0:
            journey.append(current_trip)
            current_trip = [x for x in Q[round] if x[1]==current_trip][-1][-1][0]
            round = round - 1
    TBTR_out.extend(journey)
    return set(TBTR_out)

def post_process(J, Q, destination, source, footpath_dict, inf_time, stops_dict, stoptimes_dict, print_para, d_time):
    rounds_desti_reached = [x[0] for x in list(J.items()) if x[1][0] != inf_time]
    if rounds_desti_reached == []:
        if print_para == 1:
            print('Destination cannot be reached with given transfers')
        return -1
    else:
        if print_para == 1:
            for x in reversed(rounds_desti_reached):
                last_foot_coonnect = 0
                if J[x][1][1] != (0, 0):
                    foot_time = [x for x in footpath_dict[J[x][1][1][1]] if x[0] == destination][0]
                    last_print_line = f'from {J[x][1][1][1]} walk uptil  {destination} for {foot_time[1]} minutes and reach at {J[x][0].time()}'
                    destination = J[x][1][1][1]
                    J[x][1] = (J[x][1][0], (0, 0))
                    last_foot_coonnect = 1

                round_no = x
                journey = []
                current_trip = J[x][1][0]
                while [x for x in Q[round_no] if x[2] == current_trip][0][4][0] != 0:
                    journey.append([x for x in Q[round_no] if x[2] == current_trip][-1][-1])
                    current_trip = journey[-1][0]
                    round_no = round_no - 1
                temp = [x for x in Q[round_no] if x[2] == current_trip]
                # last trip is added with -1 in previous trip index (For both footpath from source and direct bus from source)
                if temp[0][4][1] == 0:
                    # First trip is boarded from surce
                    journey.append((0, (-1, temp[0][2], temp[0][1])))
                else:
                    # take Footpath  and then board first trip
                    journey.append([0, (-1, temp[0][2], temp[0][1])])
                    too_stop = stops_dict[int(temp[0][2].split("_")[0])][temp[0][1]]
                    foot_info = [x for x in footpath_dict[source] if x[0] == too_stop][0]
                    journey.append((0, (foot_info[0], foot_info[1], d_time + foot_info[1])))

                legs = []
                from_trip = [int(x) for x in journey[0][1][1].split("_")]
                from_stop = stoptimes_dict[from_trip[0]][from_trip[1]][journey[0][1][2]]
                desti_index = stops_dict[from_trip[0]].index(destination)
                to_stop = stoptimes_dict[from_trip[0]][from_trip[1]][desti_index]
                if journey[0][1][0] != -1:
                    legs.append(
                        (0, from_stop[0], from_stop[1], to_stop[0], to_stop[1], f"{from_trip[0]}_{from_trip[1]}"))

                for idx in range(len(journey) - 2):
                    from_trip = [int(x) for x in journey[idx][0].split("_")]
                    from_stop_idx, to_stop_idx = journey[idx + 1][1][2], journey[idx][1][0]
                    from_stop = stoptimes_dict[from_trip[0]][from_trip[1]][from_stop_idx]
                    to_stop = stoptimes_dict[from_trip[0]][from_trip[1]][to_stop_idx]
                    temp = [int(x) for x in journey[idx][1][1].split("_")]
                    temp_stop_idx = journey[idx][1][2]
                    temp_stp = stops_dict[temp[0]][temp_stop_idx]
                    if to_stop[0] == temp_stp:
                        legs.append(
                            (0, from_stop[0], from_stop[1], to_stop[0], to_stop[1], f"{from_trip[0]}_{from_trip[1]}"))
                    else:
                        foot_time = [x for x in footpath_dict[to_stop[0]] if x[0] == temp_stp][0][1]
                        legs.append((1, to_stop[0], foot_time, temp_stp, to_stop[1] + foot_time))
                        temp = [int(x) for x in journey[idx + 1][1][1].split("_")]
                        temp_stop_idx = journey[idx + 1][1][2]
                        temp_stp = stops_dict[temp[0]][temp_stop_idx]
                        legs.append(
                            (0, from_stop[0], from_stop[1], to_stop[0], to_stop[1], f"{from_trip[0]}_{from_trip[1]}"))

                idx = [x for x in range(len(journey)) if journey[x][1][0] == -1][0]
                # idx is last trip index
                last_Trip = [int(x) for x in journey[idx][1][1].split("_")]
                last_Trip_board_stop = journey[idx][1][2]
                last_Trip_board_stop = stoptimes_dict[last_Trip[0]][last_Trip[1]][last_Trip_board_stop]
                legs.append((0, last_Trip_board_stop[0], last_Trip_board_stop[1], from_stop[0], from_stop[1],
                             f"{last_Trip[0]}_{last_Trip[1]}"))
                if last_Trip_board_stop[0] != source:
                    idx = idx + 1
                    legs.append((1, source, journey[idx][1][0], journey[idx][1][1], journey[idx][1][2]))

                for j_leg in reversed(legs):
                    if j_leg[0] == 0:
                        print(
                            f'from {j_leg[1]} board at {j_leg[2].time()} and get down on {j_leg[3]} at {j_leg[4].time()} along {j_leg[5]}')
                    else:
                        print(
                            f'from {j_leg[1]} walk uptil  {j_leg[3]} for {j_leg[2]} minutes and reach at {j_leg[4].time()}')
                if last_foot_coonnect == 1:
                    print(last_print_line)
                print("####################################")

        TBTR_out = []
        for x in reversed(rounds_desti_reached):
            TBTR_out.append(J[x][0])
        return TBTR_out
