"""
Module contains function related to TBTR, rTBTR, One-To-Many rTBTR, HypTBTR
"""
from collections import defaultdict
from collections import deque

import pandas as pd


def initlize_tbtr():
    '''
    Initial values for TBTR
    Returns:
        J: defaultdict to store arrival timestamps
        inf_time: Variable indicating infinite time (pandas.datetime)
    '''
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    J = defaultdict(lambda: [inf_time, 0])
    return J

def initlize_onemany(MAX_TRANSFER, destniation_list):
    '''
    Initial values for TBTR
    Returns:
        J: defaultdict to store arrival timestamps
        inf_time: Variable indicating infinite time (pandas.datetime)
    '''
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    J = {desti: {x: [inf_time, 0] for x in range(MAX_TRANSFER)} for desti in destniation_list}
    return J, inf_time


def initialize_from_desti_new(routes_by_stop_dict, stops_dict, DESTINATION, footpath_dict):
    '''
    initialize routes/footpath to DESTINATION
    Args:
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        DESTINATION: stop id (int)
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}

    Returns:
        L: A dict of format {route_id: (from_stop_idx, travel time, stop id)}
    '''
    L_dict = defaultdict(lambda: [])
    try:
        transfer_to_desti = footpath_dict[DESTINATION]
        for from_stop, foot_time in transfer_to_desti:
            try:
                walkalble_desti_route = routes_by_stop_dict[from_stop]
                for route in walkalble_desti_route:
                    L_dict[route].append((stops_dict[route].index(from_stop), foot_time, from_stop))
            except KeyError:
                pass  # Line 1 Curtailed network and full transfer file will cause error.
    except KeyError:
        pass
    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[DESTINATION]:
        L_dict[route].append((stops_dict[route].index(DESTINATION), delta_tau, DESTINATION))
    return dict(L_dict)


def initialize_from_desti_onemany(routes_by_stop_dict, stops_dict, destination_list, footpath_dict):
    '''
    initialize routes/footpath to DESTINATION
    Args:
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        DESTINATION: stop id (int)
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}

    Returns:
        L: A dict of format {route_id: (from_stop_idx, travel time, stop id)}
    '''
    L_dict_final = {}
    for DESTINATION in destination_list:
        L_dict = defaultdict(lambda: [])
        try:
            transfer_to_desti = footpath_dict[DESTINATION]
            for from_stop, foot_time in transfer_to_desti:
                try:
                    walkalble_desti_route = routes_by_stop_dict[from_stop]
                    for route in walkalble_desti_route:
                        L_dict[route].append((stops_dict[route].index(from_stop), foot_time, from_stop))
                except KeyError:
                    pass  # Line 1 Curtailed network and full transfer file will cause error.
        except KeyError:
            pass
        delta_tau = pd.to_timedelta(0, unit="seconds")
        for route in routes_by_stop_dict[DESTINATION]:
            L_dict[route].append((stops_dict[route].index(DESTINATION), delta_tau, DESTINATION))
        L_dict_final[DESTINATION] = dict(L_dict)
    return L_dict_final



def initialize_from_source_new(footpath_dict, SOURCE, routes_by_stop_dict, stops_dict, stoptimes_dict, D_TIME,
                               MAX_TRANSFER, WALKING_FROM_SOURCE):
    '''
    Initialize trips from SOURCE in std_TBTR
    Args:
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}
        SOURCE: SOURCE stop id (int)
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        D_TIME: Departure time (pandas.datetime)
        MAX_TRANSFER: Maximum transfer  (int)
        WALKING_FROM_SOURCE: 1 or 0. 1 means walking from SOURCE is allowed.

    Returns:
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
    '''
    Q = [[] for x in range(MAX_TRANSFER + 1)]
    R_t = defaultdict(lambda: 1000)
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                delta_tau = connection[1]
                walkable_source_routes = routes_by_stop_dict[connection[0]]
                for route in walkable_source_routes:
                    stop_index = stops_dict[route].index(connection[0])
                    route_trip = stoptimes_dict[route]
                    for trip_idx, trip in enumerate(route_trip):
                        if D_TIME + delta_tau <= trip[stop_index][1]:
                            _enqueue1(f'{route}_{trip_idx}', stop_index, 0, (0, connection[0]), R_t, Q,
                                      stoptimes_dict)
                            break
        except KeyError:
            pass
    #    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[SOURCE]:
        stop_index = stops_dict[route].index(SOURCE)
        route_trip = stoptimes_dict[route]
        for trip_idx, trip in enumerate(route_trip):
            #            if D_TIME + delta_tau <= trip[stop_index][1]:
            if D_TIME <= trip[stop_index][1]:
                _enqueue1(f'{route}_{trip_idx}', stop_index, 0, (0, 0), R_t, Q, stoptimes_dict)
                break
    return R_t, Q


def initialize_from_source_range(D_TIME, MAX_TRANSFER, stops_dict, stoptimes_dict, SOURCE, n, R_t):
    '''
    Initialize trips from SOURCE in rTBTR
    Args:
        D_TIME: Departure time (pandas.datetime)
        MAX_TRANSFER: Maximum transfer  (int)
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        SOURCE: Stop id (int)
        n: round ( n=0 here)
        R_t: Nested_Dict with primary keys as trip id and secondary keys as round. format {trip_id {[round]: first reached stop}}
    Returns:
        Q: Queue of trips
    '''
    Q = [[] for x in range(MAX_TRANSFER + 1)]
    route, trip_idx = [int(x) for x in D_TIME[0].split("_")]
    stop_index = D_TIME[2]
    _enqueue_range1(f'{route}_{trip_idx}', stop_index, n, (0, 0), R_t, Q, stoptimes_dict, MAX_TRANSFER)
    return Q


def _enqueue_range1(to_trip_id, to_trip_id_stop, n, pointer, R_t, Q, stoptimes_dict, MAX_TRANSFER):
    '''
    Note:(This is called by initialize_from_source_range). This will later get merged with enqueue_range2.
    Add trips to round 0 in Q and update R_t dict.
    Args:
        to_trip_id: trip id (char)
        to_trip_id_stop: stop index (int)
        n: round (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Nested_Dict with primary keys as trip id and secondary keys as round. format {trip_id {[round]: first reached stop}}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        MAX_TRANSFER: Maximum transfer  (int)
    Returns:
        None

    '''
    if to_trip_id_stop < R_t[n][to_trip_id]:
        route, tid = [int(x) for x in to_trip_id.split("_")]
        Q[n].append((to_trip_id_stop, to_trip_id, R_t[n][to_trip_id], route, tid, pointer))
        for x in range(tid, len(stoptimes_dict[route]) + 1):
            for r in range(n, MAX_TRANSFER + 1):
                R_t[r][f"{route}_{x}"] = min(R_t[r][f"{route}_{x}"], to_trip_id_stop)


def enqueue_range2(connection_list, nextround, pointer, R_t, Q, stoptimes_dict, MAX_TRANSFER):
    '''
    Main enqueue trips to add trips to next round and update R_t in rTBTR
    Args:
        connection_list: List of connections to be added. format: [ (to_trip_id, to_trip_id_stop_index), ... ]
        nextround: Round to which connections are added (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Nested_Dict with primary keys as trip id and secondary keys as round. format {trip_id {[round]: first reached stop}}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        MAX_TRANSFER: Maximum transfer  (int)

    Returns:
        None
    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[nextround][to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[nextround].append((to_trip_id_stop, to_trip_id, R_t[nextround][to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                for r in range(nextround, MAX_TRANSFER + 1):
                    new_tid = f"{route}_{x}"
                    if R_t[r][new_tid] > to_trip_id_stop:
                        R_t[r][new_tid] = to_trip_id_stop




def enqueue(connection_list, round, pointer, R_t, Q, stoptimes_dict):
    '''
    Main enqueue function used in std_TBTR to queue trips and update first reached stop of each trip.
    Args:
        connection_list: List of connections to be added. format: [ (to_trip_id, to_trip_id_stop_index), ... ]
        nextround: Round to which connections are added (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
    Returns:
        None

    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                new_tid = f"{route}_{x}"
                #                R_t[new_tid] = min(R_t[new_tid], to_trip_id_stop)
                if R_t[new_tid] > to_trip_id_stop:
                    R_t[new_tid] = to_trip_id_stop


def _enqueue1(to_trip_id, to_trip_id_stop, round, pointer, R_t, Q, stoptimes_dict):
    '''
    Note:(This is called by initialize_from_source_new). This will later get merged with enqueue2.
    Add trips to round 0 in Q and update R_t dict.
    Args:
        to_trip_id: trip id (char)
        to_trip_id_stop: stop index (int)
        n: round (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}

    Returns:
        None
    '''
    if to_trip_id_stop < R_t[to_trip_id]:
        route, tid = [int(x) for x in to_trip_id.split("_")]
        Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
        for x in range(tid, len(stoptimes_dict[route]) + 1):
            R_t[f"{route}_{x}"] = min(R_t[f"{route}_{x}"], to_trip_id_stop)




def update_label(label, round, pointer, J, MAX_TRANSFER):
    '''
    Update DESTINATION pareto set as a new journey has been found.
    Args:
        label: Arrival label (pandas.datetime)
        round: Round in which DESTINATION is reached (int)
        trip_id: Pointer for backtracking (To be developed)
        J: defaultdict to store arrival timestamps
    Returns:
        J

    '''
    J[round][1] = pointer
#    J[round][0] = label
    for x in range(round, MAX_TRANSFER):
        J[x][0] = label
    return J

def post_process_range_oldx(J, Q, rounds_desti_reached, DESTINATION):
    '''
    Contains all the post-processing features for rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal set.
    Args:
        J: defaultdict to store arrival timestamps
        Q: Queue of trips
        rounds_desti_reached: Rounds in which DESTINATION is reached. Format- [ int,int... ]
    Returns:
        TBTR_out: Trips needed to cover pareto-optimal set. (set)
    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    TBTR_out = []
    for x in reversed(rounds_desti_reached):
        round = x
        current_trip = J[x][1][0]
        journey = []
        while current_trip != 0:
            journey.append(current_trip)
            current_trip = [x for x in Q[round] if x[1] == current_trip][-1][-1][0]
            round = round - 1
        TBTR_out.extend(journey)
    return TBTR_out

def post_process_range(J, Q, rounds_desti_reached):
    '''
    Contains all the post-processing features for rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal set.
    Args:
        J: defaultdict to store arrival timestamps
        Q: Queue of trips
        rounds_desti_reached: Rounds in which DESTINATION is reached. Format- [ int,int... ]
    Returns:
        TBTR_out: Trips needed to cover pareto-optimal set. (set)
    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    TBTR_out = []
    for x in reversed(rounds_desti_reached):
        round = x
        current_trip = J[x][1][0]
        journey = []
        while current_trip != 0:
            journey.append(current_trip)
            current_trip = [x for x in Q[round] if x[1] == current_trip][-1][-1][0]
            round = round - 1
        TBTR_out.extend(journey)
    return set(TBTR_out)

def post_process_range_onemany(J, Q, rounds_desti_reached, desti):
    '''
    Contains all the post-processing features for rTBTR.
    Currently supported functionality:
        Collect list of trips needed to cover pareto-optimal set.
    Args:
        J: defaultdict to store arrival timestamps
        Q: Queue of trips
        rounds_desti_reached: Rounds in which DESTINATION is reached. Format- [ int,int... ]
    Returns:
        TBTR_out: Trips needed to cover pareto-optimal set. (set)
    '''
    rounds_desti_reached = list(set(rounds_desti_reached))
    TBTR_out = []
    for x in reversed(rounds_desti_reached):
        round = x
        current_trip = J[desti][x][1][0]
        journey = []
        while current_trip != 0:
            journey.append(current_trip)
            current_trip = [x for x in Q[round] if x[1] == current_trip][-1][-1][0]
            round = round - 1
        TBTR_out.extend(journey)
    return set(TBTR_out)


def post_process_old(J, Q, DESTINATION, SOURCE, footpath_dict, inf_time, stops_dict, stoptimes_dict, PRINT_PARA, D_TIME):
    '''
    Contains all the post-processing features for std_TBTR.
    Currently supported functionality:
        Collect pareto-optimal arrival timestamps.
    Args:
        J: defaultdict to store arrival timestamps
        Q: Queue of trips
        DESTINATION: DESTINATION stop id (int)
        SOURCE: SOURCE stop id (int)
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}
        inf_time: Variable indicating infinite time (pandas.datetime)
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        PRINT_PARA: 1 or 0. 1 mens print complete path (int)
        D_TIME: Departure time (pandas.datetime)
    Returns:
        TBTR_out: pareto-optimal arrival timestamps. format = [(pandas.datetime),(pandas.datetime)... ]

    '''
    rounds_desti_reached = [x[0] for x in list(J.items()) if x[1][0] != inf_time]
    if rounds_desti_reached == []:
        if PRINT_PARA == 1:
            print('DESTINATION cannot be reached with given transfers')
        return -1
    else:
        if PRINT_PARA == 1:
            for x in reversed(rounds_desti_reached):
                last_foot_coonnect = 0
                if J[x][1][1] != (0, 0):
                    foot_time = [x for x in footpath_dict[J[x][1][1][1]] if x[0] == DESTINATION][0]
                    last_print_line = f'from {J[x][1][1][1]} walk uptil  {DESTINATION} for {foot_time[1]} minutes and reach at {J[x][0].time()}'
                    DESTINATION = J[x][1][1][1]
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
                # last trip is added with -1 in previous trip index (For both footpath from SOURCE and direct bus from SOURCE)
                if temp[0][4][1] == 0:
                    # First trip is boarded from surce
                    journey.append((0, (-1, temp[0][2], temp[0][1])))
                else:
                    # take Footpath  and then board first trip
                    journey.append([0, (-1, temp[0][2], temp[0][1])])
                    too_stop = stops_dict[int(temp[0][2].split("_")[0])][temp[0][1]]
                    foot_info = [x for x in footpath_dict[SOURCE] if x[0] == too_stop][0]
                    journey.append((0, (foot_info[0], foot_info[1], D_TIME + foot_info[1])))

                legs = []
                from_trip = [int(x) for x in journey[0][1][1].split("_")]
                from_stop = stoptimes_dict[from_trip[0]][from_trip[1]][journey[0][1][2]]
                desti_index = stops_dict[from_trip[0]].index(DESTINATION)
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
                if last_Trip_board_stop[0] != SOURCE:
                    idx = idx + 1
                    legs.append((1, SOURCE, journey[idx][1][0], journey[idx][1][1], journey[idx][1][2]))

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

def post_process(J, Q, DESTINATION, SOURCE, footpath_dict, stops_dict, stoptimes_dict, PRINT_PARA, D_TIME, MAX_TRANSFER):
    '''
    Contains all the post-processing features for std_TBTR.
    Currently supported functionality:
        Collect pareto-optimal arrival timestamps.
    Args:
        J: defaultdict to store arrival timestamps
        Q: Queue of trips
        DESTINATION: DESTINATION stop id (int)
        SOURCE: SOURCE stop id (int)
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}
        inf_time: Variable indicating infinite time (pandas.datetime)
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        PRINT_PARA: 1 or 0. 1 mens print complete path (int)
        D_TIME: Departure time (pandas.datetime)
    Returns:
        TBTR_out: pareto-optimal arrival timestamps. format = [(pandas.datetime),(pandas.datetime)... ]

    '''
    rounds_desti_reached = [roundno for roundno in range(0, MAX_TRANSFER) if J[roundno][1] != 0]
    if rounds_desti_reached == []:
        if PRINT_PARA == 1:
            print('DESTINATION cannot be reached with given transfers')
        return -1
    else:
        if PRINT_PARA == 1:
            for x in reversed(rounds_desti_reached):
                last_foot_coonnect = 0
                if J[x][1][1] != (0, 0):
                    foot_time = [x for x in footpath_dict[J[x][1][1][1]] if x[0] == DESTINATION][0]
                    last_print_line = f'from {J[x][1][1][1]} walk uptil  {DESTINATION} for {foot_time[1]} minutes and reach at {J[x][0].time()}'
                    DESTINATION = J[x][1][1][1]
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
                # last trip is added with -1 in previous trip index (For both footpath from SOURCE and direct bus from SOURCE)
                if temp[0][4][1] == 0:
                    # First trip is boarded from surce
                    journey.append((0, (-1, temp[0][2], temp[0][1])))
                else:
                    # take Footpath  and then board first trip
                    journey.append([0, (-1, temp[0][2], temp[0][1])])
                    too_stop = stops_dict[int(temp[0][2].split("_")[0])][temp[0][1]]
                    foot_info = [x for x in footpath_dict[SOURCE] if x[0] == too_stop][0]
                    journey.append((0, (foot_info[0], foot_info[1], D_TIME + foot_info[1])))

                legs = []
                from_trip = [int(x) for x in journey[0][1][1].split("_")]
                from_stop = stoptimes_dict[from_trip[0]][from_trip[1]][journey[0][1][2]]
                desti_index = stops_dict[from_trip[0]].index(DESTINATION)
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
                if last_Trip_board_stop[0] != SOURCE:
                    idx = idx + 1
                    legs.append((1, SOURCE, journey[idx][1][0], journey[idx][1][1], journey[idx][1][2]))

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



"""
##############################   Deprecated Functions   ##############################

def initlize_old():
    '''
    Initial values for TBTR
    Returns:
        J: defaultdict to store arrival timestamps
        inf_time: Variable indicating infinite time (pandas.datetime)
    '''
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    J = defaultdict(lambda: [inf_time, 0])
    return J, inf_time

def initlize(MAX_TRANSFER):
    '''
    Initial values for TBTR
    Returns:
        J: defaultdict to store arrival timestamps
        inf_time: Variable indicating infinite time (pandas.datetime)
    '''
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    J = {x:[inf_time, 0] for x in range(MAX_TRANSFER)}
#    J = defaultdict(lambda: [inf_time, 0])
    return J



def initialize_from_desti_old(transfers_file, routes_by_stop_dict, stops_dict, DESTINATION):
    '''
    Depreciated now (initialize_from_desti > initialize_from_desti_new).
    Uses transfers_file to get connections to DESTINATION. ( Upgraded to transfer dict as footpaths are transitive)
    Args:
        transfers_file: GTFS transfer file
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        DESTINATION: stop id (int)

    Returns:
        l: A list of format [(route id, from_stop_idx, time, stop id)]
    '''
    L = []
    transfer_to_desti = transfers_file[transfers_file.to_stop_id == DESTINATION][['from_stop_id', 'min_transfer_time']]
    for _, row in transfer_to_desti.iterrows():
        delta_tau = pd.to_timedelta(row.min_transfer_time, unit="seconds")
        try:
            walkalble_desti_route = routes_by_stop_dict[row.from_stop_id]
            for route in walkalble_desti_route:
                L.append((route, stops_dict[route].index(row.from_stop_id), delta_tau))
        except KeyError:
            pass  # Line 1 Curtailed network and full transfer file will cause error.
    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[DESTINATION]:
        L.append((route, stops_dict[route].index(DESTINATION), delta_tau))
    return L

def initialize_from_desti(routes_by_stop_dict, stops_dict, DESTINATION, footpath_dict):
    '''
    Depreciated now (initialize_from_desti < initialize_from_desti_new).
    Maintains L as list (Upgraded to dict)
    Args:
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        DESTINATION: stop id (int)
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}

    Returns:
        l: A list of format [(route id, from_stop_idx, time, stop id)]
    '''
    L = []
    try:
        transfer_to_desti = footpath_dict[DESTINATION]
        for from_stop, foot_time in transfer_to_desti:
            try:
                walkalble_desti_route = routes_by_stop_dict[from_stop]
                for route in walkalble_desti_route:
                    L.append((route, stops_dict[route].index(from_stop), foot_time, from_stop))
            except KeyError:
                pass  # Line 1 Curtailed network and full transfer file will cause error.
    except KeyError:
        pass
    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[DESTINATION]:
        L.append((route, stops_dict[route].index(DESTINATION), delta_tau, DESTINATION))
    return L

def initialize_from_desti4(routes_by_stop_dict, stops_dict, destination_list, footpath_dict):
    '''
    Depreciated now (initialize_from_desti < initialize_from_desti_new).
    Maintains L as list (Upgraded to dict)
    Args:
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        DESTINATION: stop id (int)
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}

    Returns:
        l: A list of format [(route id, from_stop_idx, time, stop id)]
    '''
    L = {}
    for DESTINATION in destination_list:
        L[DESTINATION] = []
        try:
            transfer_to_desti = footpath_dict[DESTINATION]
            for from_stop, foot_time in transfer_to_desti:
                try:
                    walkalble_desti_route = routes_by_stop_dict[from_stop]
                    for route in walkalble_desti_route:
                        L[DESTINATION].append((route, stops_dict[route].index(from_stop), foot_time, from_stop))
                except KeyError:
                    pass  # Line 1 Curtailed network and full transfer file will cause error.
        except KeyError:
            pass
        delta_tau = pd.to_timedelta(0, unit="seconds")
        for route in routes_by_stop_dict[DESTINATION]:
            L[DESTINATION].append((route, stops_dict[route].index(DESTINATION), delta_tau, DESTINATION))
    return L

def initialize_from_source(footpath_dict, SOURCE, routes_by_stop_dict, stops_dict, stoptimes_dict, D_TIME, MAX_TRANSFER, WALKING_FROM_SOURCE):
    '''
    Depreciated now (initialize_from_source > initialize_from_source_new).
    Uses Old enqueu function. ( Upgrade uses new enqueu function )
    Args:
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}
        SOURCE: SOURCE stop id (int)
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        stops_dict: Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
        D_TIME: Departure time (pandas.datetime)
        MAX_TRANSFER: Maximum transfer  (int)
        WALKING_FROM_SOURCE: 1 or 0. 1 means walking from SOURCE is allowed.

    Returns:
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips

    '''
    Q = [deque() for x in range(MAX_TRANSFER + 1)]
    R_t = defaultdict(lambda: 1000)
    if WALKING_FROM_SOURCE == 1:
        try:
            source_footpaths = footpath_dict[SOURCE]
            for connection in source_footpaths:
                delta_tau = connection[1]
                walkable_source_routes = routes_by_stop_dict[connection[0]]
                for route in walkable_source_routes:
                    stop_index = stops_dict[route].index(connection[0])
                    route_trip = stoptimes_dict[route]
                    for trip_idx, trip in enumerate(route_trip):
                        if D_TIME + delta_tau <= trip[stop_index][1]:
                            enqueue(f'{route}_{trip_idx}', stop_index, 0, (0, connection[0]), R_t, Q, stoptimes_dict)
                            break
        except KeyError:
            pass
    #    delta_tau = pd.to_timedelta(0, unit="seconds")
    for route in routes_by_stop_dict[SOURCE]:
        stop_index = stops_dict[route].index(SOURCE)
        route_trip = stoptimes_dict[route]
        for trip_idx, trip in enumerate(route_trip):
            #            if D_TIME + delta_tau <= trip[stop_index][1]:
            if D_TIME <= trip[stop_index][1]:
                enqueue(f'{route}_{trip_idx}', stop_index, 0, (0, 0), R_t, Q, stoptimes_dict)
                break
    return R_t, Q


def hyper_enqueue(connection_list, round, pointer, R_t, Q, stoptimes_dict, final_trips):
    '''
    Main enqueue function used in std_TBTR to queue trips and update first reached stop of each trip.
    Args:
        connection_list: List of connections to be added. format: [ (to_trip_id, to_trip_id_stop_index), ... ]
        nextround: Round to which connections are added (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
    Returns:
        None

    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id in final_trips and to_trip_id_stop < R_t[to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                new_tid = f"{route}_{x}"
                #                R_t[new_tid] = min(R_t[new_tid], to_trip_id_stop)
                if R_t[new_tid] > to_trip_id_stop:
                    R_t[new_tid] = to_trip_id_stop

def update_label_old(label, round, pointer, J):
    '''
    Update DESTINATION pareto set as a new journey has been found.
    Args:
        label: Arrival label (pandas.datetime)
        round: Round in which DESTINATION is reached (int)
        trip_id: Pointer for backtracking (To be developed)
        J: defaultdict to store arrival timestamps
    Returns:
        J

    '''
    if J[round][0] > label:
        J[round][0] = label
        J[round][1] = pointer
    return J



def enqueue(to_trip_id, to_trip_id_stop, round, pointer, R_t, Q, stoptimes_dict):
    '''
    Depreciated now (enqueue > _enqueue1 and enqueue2 ).
    First enqueue function. No longer supported.
    Args:
        to_trip_id: trip id (char)
        to_trip_id_stop: stop index (int)
        n: round (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
    Returns:
        None
    '''
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


def enqueue2(connection_list, round, pointer, R_t, Q, stoptimes_dict):
    '''
    Main enqueue function used in std_TBTR to queue trips and update first reached stop of each trip.
    Args:
        connection_list: List of connections to be added. format: [ (to_trip_id, to_trip_id_stop_index), ... ]
        nextround: Round to which connections are added (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
    Returns:
        None
    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                R_t[f"{route}_{x}"] = min(to_trip_id_stop, R_t[f"{route}_{x}"])





def enqueue3(connection_list, round, pointer, R_t, Q, stoptimes_dict):
    '''
    Main enqueue function used in std_TBTR to queue trips and update first reached stop of each trip.
    Args:
        connection_list: List of connections to be added. format: [ (to_trip_id, to_trip_id_stop_index), ... ]
        nextround: Round to which connections are added (int)
        pointer: Pointer for backtracking journey ( To be developed )
        R_t: Dict with keys as trip id. format - {trip_id : first reached stop}
        Q: Queue of trips
        stoptimes_dict: Pre-processed dict- format {route_id: [[trip1], [trip1]]}
    Returns:
        None

    '''
    for to_trip_id, to_trip_id_stop in connection_list:
        if to_trip_id_stop < R_t[to_trip_id]:
            route, tid = [int(x) for x in to_trip_id.split("_")]
            Q[round].append((to_trip_id_stop, to_trip_id, R_t[to_trip_id], route, tid, pointer))
            for x in range(tid, len(stoptimes_dict[route]) + 1):
                new_tid = f"{route}_{x}"
#                R_t[new_tid] = min(R_t[new_tid], to_trip_id_stop)
                if R_t[new_tid] > to_trip_id_stop:
                    R_t[new_tid] = to_trip_id_stop


"""

