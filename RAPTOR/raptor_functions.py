"""
Module contains function related to RAPTOR, rRAPTOR, One-To-Many rRAPTOR, HypRAPTOR
"""
from collections import deque as deque

import pandas as pd


################################################################################################################################################################################################

def initlize_raptor(routes_by_stop_dict, SOURCE, transfer):
    '''
    Initialize values for RAPTOR.
    Args:
        routes_by_stop_dict (dict): Pre-processed dict- format {stop_id: [routes]}
        SOURCE (int): SOURCE stop id
        transfer (int): Max transfer limit
    Returns:
        marked_stop (Deque): Deque to store marked stop
        label (dict): Nested dict to maintain label {round : {stop_id: pandas.datetime}}
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}
        star_label (dict): dict to maintain best arrival label {stop id: pandas.datetime}
        inf_time (pd.timestamp): Variable indicating infinite time (pandas.datetime)
    '''
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)

    pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, transfer + 1)}
    label = {x: {stop: inf_time for stop in routes_by_stop_dict.keys()} for x in range(0, transfer + 1)}
    star_label = {stop: inf_time for stop in routes_by_stop_dict.keys()}

    marked_stop = deque()
    marked_stop.append(SOURCE)
    return (marked_stop, label, pi_label, star_label, inf_time)


def check_stop_validity(stops, SOURCE, DESTINATION):
    '''
    Check if the entered SOURCE and DESTINATION stop id are present in stop list or not.
    Args:
        stops: GTFS stops.txt
        SOURCE (int): SOURCE stop id
        DESTINATION (int): DESTINATION stop id
    Returns:
        None
    '''
    if SOURCE in stops.stop_id and DESTINATION in stops.stop_id:
        print('correct inputs')
    else:
        print("incorrect inputs")


##################################################################################################################################################################################################
# N##ote3:A route(stops 1 to 20) may contain 2 trip pattern with trip 1 from 1 to 10 and trip 2  from 10 to 20.  I want earliest trip from 10 after 11pm. Now Trip 1
# may end at 10 at 12pm thus stop 10 has time stamp greater than 10 but I cannot hop on this trip from stop 10. Technically this is coz  we should use dep_time
# for finding trip and for such a case dep_time would not be defined for ending station. For now dep_time is populated same is arrival time everywhere. Trip[:1] skips
# the last element and thus takes care of this
# Note:(Not Correct now i gues.. coz on one route bus might not be defined but it might be on other routes.) get_latest_trip may produce error 'local variable 'current_trip' referenced before assignment' coz if the SOURCE stop is  2 then  there is no bus from it after 9AM.
# Thus, it may cause error if the deaprting time is after 9Am at stop 2. To avoid it, intilize the departing time early like 6 Am. This
# Also. from stop zero there first bus is at 6AM. If the departing time is 5Am , that is taken care of(meaning itll give earliest trip at that stop as that of 6 Am)
####Call:get_latest_trip(route,p_i,d_time_at_pi)
# d_time_at_pi=previous_arrival_at_pi
# stoptimes_dict[22543][0]
def get_latest_trip_new(stoptimes_dict, route, arrival_time_at_pi, pi_index, change_time):
    '''
    Get latest trip after a certain timestamp from the given stop of a route.
    Args:
        stoptimes_dict (dict): Pre-processed dict- format {route_id: [[trip_1], [trip_2]]}
        route (int): Route-id
        arrival_time_at_pi (pandas.datetime): Arrival time at stop pi_index
        pi_index (int): stop index of the boarding stop on the route.
        change_time (pandas.datetime): Change time
    Returns:
        If a trip exists:
            trip index , Trip
        else:
            -1,-1   (e.g. when there is no trip after the given timestamp)
    '''
#    arrival_time_at_pi, pi_index =  label[k - 1][p_i], current_stopindex_by_route
    try:
        for trip_idx, trip in enumerate(stoptimes_dict[route]):
            if trip[pi_index][1] >= arrival_time_at_pi + change_time:
                return f'{route}_{trip_idx}', stoptimes_dict[route][trip_idx]
        return -1, -1  # No trip is found after arrival_time_at_pi
    except KeyError:
        return -1, -1  # NO trip exsist for this route. in this case check tripid from trip file for this route and then look waybill.ID. Likely that trip is across days thats why it is rejected in stoptimes builder while checking



def post_processing(DESTINATION, pi_label, PRINT_PARA, label):
    '''
    Post processing for std_RAPTOR. Currently supported functionality:
        1. Rounds in which DESTINATION is reached
        2. Trips for covering pareto optimal set
        3. Pareto optimal timestamps.
    Args:
        DESTINATION (int): DESTINATION stop id
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}
        PRINT_PARA (int): 1 or 0. 1 means print complete path
        label (dict): Nested dict to maintain label {round : {stop_id: pandas.datetime}}
    Returns:
        rounds_inwhich_desti_reached (list): List of rounds in which DESTINATION is reached. Format - [int, int...]
        trip_set (list): List of rounds in which DESTINATION is reached. Format - [char, char...]
        rap_out (list): pareto-optimal arrival timestamps. format = [(pandas.datetime),(pandas.datetime)... ]

    '''
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]

    if rounds_inwhich_desti_reached == []:
        if PRINT_PARA == 1:
            print('DESTINATION cannot be reached with given MAX_TRANSFERs')
        return -1, -1, -1
    else:
        rounds_inwhich_desti_reached.reverse()
        pareto_set = []
        trip_set = []
        rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
        for k in rounds_inwhich_desti_reached:
            transfer_needed = k - 1
            journey = []
            stop = DESTINATION
            while pi_label[k][stop] != -1:
                journey.append(pi_label[k][stop])
                mode = pi_label[k][stop][0]
                if mode == 'walking':
                    stop = pi_label[k][stop][1]
                else:
                    trip_set.append(pi_label[k][stop][-1])
                    stop = pi_label[k][stop][1]
                    k = k - 1
            journey.reverse()
            pareto_set.append((transfer_needed, journey))

        if PRINT_PARA == 1:
            _print_Journey_legs(pareto_set)
        #        _save_routesExplored(save_routes, routes_exp)
        return rounds_inwhich_desti_reached, trip_set, rap_out


def _print_Journey_legs(pareto_journeys):
    '''
    Prints journey in correct format. Parent Function: post_processing
    Args:
        pareto_journeys (list): pareto optimal set.
    Returns:
        None
    '''
    for _, journey in pareto_journeys:
        for leg in journey:
            if leg[0] == 'walking':
                print(f'from {leg[1]} walk uptil  {leg[2]} for {leg[3]} minutes and reach at {leg[4].time()}')
            else:
                print(
                    f'from {leg[1]} board at {leg[0].time()} and get down on {leg[2]} at {leg[3].time()} along {leg[-1]}')
        print("####################################")


def post_processing_onetomany_rraptor(DESTINATION_LIST, pi_label, PRINT_PARA, optimized):
    '''
    post processing for Ont-To-Many rRAPTOR. Currently supported functionality:
        1. Print the output
        2. Routes required for covering pareto-optimal set.
        3. Trips required for covering pareto-optimal set.
    Args:
        DESTINATION_LIST (list): list of DESTINATION stop id. Format: [stop_id, stop_id]
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id. Format- {round : {stop_id: pointer_label}}
        PRINT_PARA (int): 1 or 0. 1 means print complete journeys
        optimized (int): 1 or 0. 1 means collect trips required for optimal journeys , 0 means collect routes
    Returns:
        if optimized==1:
            final_trips (list): List of trips required to cover all pareto-optimal journeys. format - [trip_id, trip_id...]
        else:
            final_routes (list): List of routes required to cover all pareto-optimal journeys. format - [route_id, route_id...]
    '''
    if optimized==1:
        final_trips = []
        for DESTINATION in DESTINATION_LIST:
            rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
            if rounds_inwhich_desti_reached:
                rounds_inwhich_desti_reached.reverse()
                trip_set = []
                for k in rounds_inwhich_desti_reached:
                    stop = DESTINATION
                    while pi_label[k][stop] != -1:
                        mode = pi_label[k][stop][0]
                        if mode == 'walking':
                            stop = pi_label[k][stop][1]
                        else:
                            trip_set.append(pi_label[k][stop][-1])
                            stop = pi_label[k][stop][1]
                            k = k - 1
                final_trips.extend(trip_set)
        return list(set(final_trips))
    else:
        final_routes = []
        for DESTINATION in DESTINATION_LIST:
            rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
            if rounds_inwhich_desti_reached == []:
                if PRINT_PARA == 1:
                    print('DESTINATION cannot be reached with given MAX_TRANSFERs')
            else:
                rounds_inwhich_desti_reached.reverse()
                pareto_set = []
                trip_set = []
                #            rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
                for k in rounds_inwhich_desti_reached:
                    transfer_needed = k - 1
                    journey = []
                    stop = DESTINATION
                    while pi_label[k][stop] != -1:
                        journey.append(pi_label[k][stop])
                        mode = pi_label[k][stop][0]
                        if mode == 'walking':
                            stop = pi_label[k][stop][1]
                        else:
                            trip_set.append(pi_label[k][stop][-1])
                            stop = pi_label[k][stop][1]
                            k = k - 1
                    journey.reverse()
                    pareto_set.append((transfer_needed, journey))
                    if PRINT_PARA == 1:
                        _print_Journey_legs(pareto_set)
                    for trip in trip_set:
                        final_routes.append(int(trip.split("_")[0]))
        return list(set(final_routes))




def post_processing_rraptor(DESTINATION, pi_label, PRINT_PARA, label, OPTIMIZED):
    '''
    Full post processing for rRAPTOR. Currently supported functionality:
        1. Print the output
        2. Routes required for covering pareto-optimal journeys.
        3. Trips required for covering pareto-optimal journeys.
    Args:
        DESTINATION (int): DESTINATION stop id
        pi_label (dict): Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id. Format- {round : {stop_id: pointer_label}}
        PRINT_PARA (int): 1 or 0. 1 means print complete path
        label (dict): Nested dict to maintain label {round : {stop_id: pandas.datetime}}
        optimized (int): 1 or 0. 1 means collect trips required for optimal journeys , 0 means collect routes
    Returns:
        if optimized==1:
            final_trips (list): List of trips required to cover all pareto-optimal journeys. Format - [trip_id, trip_id...]
        else:
            final_routes (list): List of routes required to cover all pareto-optimal journeys. Format - [route_id, route_id...]
    '''
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
    if OPTIMIZED==1:
        final_trip = []
        if rounds_inwhich_desti_reached:
            rounds_inwhich_desti_reached.reverse()
            for k in rounds_inwhich_desti_reached:
                stop = DESTINATION
                while pi_label[k][stop] != -1:
                    mode = pi_label[k][stop][0]
                    if mode == 'walking':
                        stop = pi_label[k][stop][1]
                    else:
                        final_trip.append(pi_label[k][stop][-1])
                        stop = pi_label[k][stop][1]
                        k = k - 1
        return list(set(final_trip))
    else:
        final_routes = []
        if rounds_inwhich_desti_reached == []:
            if PRINT_PARA == 1:
                print('DESTINATION cannot be reached with given MAX_TRANSFERs')
            return final_routes
        else:
            rounds_inwhich_desti_reached.reverse()
            pareto_set = []
            trip_set = []
            rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
            for k in rounds_inwhich_desti_reached:
                transfer_needed = k - 1
                journey = []
                stop = DESTINATION
                while pi_label[k][stop] != -1:
                    journey.append(pi_label[k][stop])
                    mode = pi_label[k][stop][0]
                    if mode == 'walking':
                        stop = pi_label[k][stop][1]
                    else:
                        trip_set.append(pi_label[k][stop][-1])
                        stop = pi_label[k][stop][1]
                        k = k - 1
                journey.reverse()
                pareto_set.append((transfer_needed, journey))
                if PRINT_PARA == 1:
                    _print_Journey_legs(pareto_set)
                for trip in trip_set:
                    final_routes.append(int(trip.split("_")[0]))
        return final_routes

"""
##############################   Deprecated Functions   ##############################
def build_odpair_from_etm():
    '''
    Build OD pairs using BMTC ETM data.
    Default ETM month: Oct, 2019
    Returns:
        list of od-pairs
    '''
    from collections import Counter
    od_pairs = pd.read_csv(r"D:\prateek\research\indivisual\BGTFS\raw_data\2019_etm\aug\etm_aug_19_STOPS.csv",
                           usecols=["till_bus_stop_id", "from_bus_stop_id"])
    od_pairs.fillna(0, inplace=True)
    od_pairs = od_pairs[(od_pairs["till_bus_stop_id"] != 0) & (od_pairs["from_bus_stop_id"] != 0)]

    od_pairs[["till_bus_stop_id", "from_bus_stop_id"]] = od_pairs[["till_bus_stop_id", "from_bus_stop_id"]].astype(int)
    od_pairs_list = list(od_pairs["till_bus_stop_id"])
    od_pairs_list.extend(list(od_pairs["from_bus_stop_id"]))
    temp = dict(Counter(od_pairs_list))

    temp = temp.items()
    temp = sorted(temp, key=lambda x: x[1], reverse=True)
    temp1 = [(int(float(x[0])), x[1]) for x in temp]
    pd.DataFrame(temp1, columns=["stops", "frequency"]).to_csv(
        r"D:\prateek\research\indivisual\Raptor\ideal_gtfs_raptor\od_pairs_freq_db.csv", index=False)
    temp2 = [x[0] for x in temp]
    pd.DataFrame(temp2, columns=["stops"]).to_csv(
        r"D:\prateek\research\indivisual\Raptor\ideal_gtfs_raptor\od_pairs_aug.csv", index=False)


def get_stop_name(id):
    '''
    Prints Bus stop name based in Stop id.
    Args:
        id: Stop id (int)
    Returns:
        None.
    '''
    bus_stop = pd.read_csv(
        "D:/prateek/research/indivisual/BGTFS/raw_data/OneDrive_2020-03-14/Data Documentation/latest data/bus_stop.csv",
        usecols=['bus_stop_id', "bus_stop_name"])
    print(bus_stop[bus_stop["bus_stop_id"] == id]["bus_stop_name"])


def initlize(routes_by_stop_dict, SOURCE, transfer):
    '''
    Args:
        routes_by_stop_dict: Pre-processed dict- format {stop_id: [routes]}
        SOURCE: SOURCE stop id (int)
        transfer: Max transfer limit (int)
    Returns:
        marked_stop: Deque to store marked stop
        label: Nested dict to maintain label {round : {stop_id: pandas.datetime}}
        pi_label: Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}
        star_label: dict to maintain best arrival label {stop id: pandas.datetime}
        inf_time: Variable indicating infinite time (pandas.datetime)
    '''
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    
    pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, transfer + 1)}
    label = {x: {stop: inf_time for stop in routes_by_stop_dict.keys()} for x in range(0, transfer + 1)}
    star_label = {stop: inf_time for stop in routes_by_stop_dict.keys()}
    
    marked_stop = deque()
    marked_stop.append(SOURCE)
    return (marked_stop, label, pi_label, star_label, inf_time)

def draw_output(journey_list):
    '''
    Draw RAPTOR output (depreciated)
    Args:
        journey_list: Pareto_optiaml journey.
    Returns:
        None
    '''
    import networkx as nx, matplotlib.pyplot as plt
    journey = journey_list
    edges = []
    edge_labels = {}
    for leg in journey:
        if leg[0] == 'walking':
            edges.append([f'{leg[1]}', f'{leg[2]}'])
            edge_labels[(f'{leg[1]}', f'{leg[2]}')] = f' ({leg[3]})-- W --{leg[4].time()}'
        else:
            edges.append([f'{leg[1]}', f'{leg[2]}'])
            edge_labels[(f'{leg[1]}', f'{leg[2]}')] = f' {leg[0].time()} --B--{leg[3].time()}'
    G = nx.DiGraph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1, node_size=500, node_color='pink', alpha=0.9,
            labels={node: node for node in G.nodes()})
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.axis('off')
    return plt.show()


def update_record(SOURCE, DESTINATION, pareto_set, D_TIME, output_list):
    '''
    Used to back tracking. (depreciated)
    Args:
        SOURCE:
        DESTINATION:
        pareto_set:
        D_TIME:
        output_list:

    Returns:
        Updated records.

    '''
    j = []
    for trnsfer, journey in pareto_set:
        temp = {}
        temp["SOURCE"] = SOURCE
        temp["desti"] = DESTINATION
        temp["query_time"] = D_TIME.time()
        temp["departure_time"] = journey[0][0].time()
        total_time = _calculate_tt(journey)
        temp["TT"] = total_time
        temp["wait_time"] = _waiting_time(journey, D_TIME)
        temp["transfer"] = trnsfer
        temp["IVTT"] = 0
        temp["OVTT"] = 0
        IVTT_time = _calcuLATE_ivtt(journey)
        temp["IVTT"] = IVTT_time
        temp["OVTT"] = total_time - IVTT_time
        j.append(temp)
    output_list.extend(j)


def _calculate_tt(journey):
    '''
    Parent function- update_record. depreciated.
    '''
    return round((pd.to_timedelta(journey[-1][-1] - journey[0][0])).total_seconds() / 60, 2)


def _waiting_time(journey, D_TIME):
    '''
    Parent function- update_record. depreciated.
    '''
    return round((pd.to_timedelta(journey[0][0] - D_TIME)).total_seconds() / 60, 2)


def _calcuLATE_ivtt(journey):
    '''
    Parent function- update_record. depreciated.
    '''
    IVTT = 0
    for leg in range(len(journey)):
        if type(journey[leg][0]) != str:
            IVTT = IVTT + (journey[leg][3] - journey[leg][0]).total_seconds()
    return round(IVTT / 60, 2)


def _save_routesExplored(save_routes, routes_exp):
    '''
    Parent function- post_processing. To be depreciated.
    Saves the route explored during RAPTOR run.
    Args:
        save_routes: 1 or 0. Save only if 1
        routes_exp: Dict of routes explored during each round.
    Returns:
        None
    '''
    if save_routes == 1:
        temp = []
        for x in routes_exp.items():
            temp.extend(list(zip([x[0] for y in x[1]], x[1])))
        pd.DataFrame(temp, columns=['round', 'route']).to_csv(r'./routes_exp_orig.csv', index=False)



def post_processing_onetomany_rraptor_partial(destination_list, pi_label):
    '''
    Partial Post processing for rRAPTOR. (Only collect the trips required for covering pareto-optimal set)
    Args:
        DESTINATION: DESTINATION stop id (int)
        pi_label: Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}

    Returns:
        trip_set: trips required for covering pareto_optimal set. format- [char, char...]
    '''
    final_trips = []
    for DESTINATION in destination_list:
        rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
        if rounds_inwhich_desti_reached:
            rounds_inwhich_desti_reached.reverse()
            trip_set = []
            for k in rounds_inwhich_desti_reached:
                stop = DESTINATION
                while pi_label[k][stop] != -1:
                    mode = pi_label[k][stop][0]
                    if mode == 'walking':
                        stop = pi_label[k][stop][1]
                    else:
                        trip_set.append(pi_label[k][stop][-1])
                        stop = pi_label[k][stop][1]
                        k = k - 1
            final_trips.extend(trip_set)
    return final_trips



def post_processing_onetomany_rraptor_full(destination_list, pi_label, PRINT_PARA):
    '''
    Full post processing for rRAPTOR. Currently supported functionality:
        1. Print the output
        2. Routes required for covering pareto-optimal set.
        3. Trips required for covering pareto-optimal set.
    Args:
        DESTINATION: DESTINATION stop id (int)
        pi_label: Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}
        PRINT_PARA: 1 or 0. 1 means print complete path (int)
        label: Nested dict to maintain label {round : {stop_id: pandas.datetime}}
        route_set: Set to store routes required for covering pareto-optimal label.

    Returns:
        route_set: Set to store routes required for covering pareto-optimal label. format - {int, int...}

    '''
    final_routes = []
    for DESTINATION in destination_list:
        rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]

        if rounds_inwhich_desti_reached == []:
            if PRINT_PARA == 1:
                print('DESTINATION cannot be reached with given MAX_TRANSFERs')
        else:
            rounds_inwhich_desti_reached.reverse()
            pareto_set = []
            trip_set = []
#            rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
            for k in rounds_inwhich_desti_reached:
                transfer_needed = k - 1
                journey = []
                stop = DESTINATION
                while pi_label[k][stop] != -1:
                    journey.append(pi_label[k][stop])
                    mode = pi_label[k][stop][0]
                    if mode == 'walking':
                        stop = pi_label[k][stop][1]
                    else:
                        trip_set.append(pi_label[k][stop][-1])
                        stop = pi_label[k][stop][1]
                        k = k - 1
                journey.reverse()
                pareto_set.append((transfer_needed, journey))
                if PRINT_PARA == 1:
                    _print_Journey_legs(pareto_set)
                for trip in trip_set:
                    final_routes.append(int(trip.split("_")[0]))
    return final_routes

def post_processing_rraptor_partial(DESTINATION, pi_label):
    '''
    Partial Post processing for rRAPTOR. (Only collect the trips required for covering pareto-optimal set)
    Args:
        DESTINATION: DESTINATION stop id (int)
        pi_label: Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}

    Returns:
        trip_set: trips required for covering pareto_optimal set. format- [char, char...]
    '''
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]
    if rounds_inwhich_desti_reached == []:
        return []
    else:
        rounds_inwhich_desti_reached.reverse()
        trip_set = []
        for k in rounds_inwhich_desti_reached:
            stop = DESTINATION
            while pi_label[k][stop] != -1:
                mode = pi_label[k][stop][0]
                if mode == 'walking':
                    stop = pi_label[k][stop][1]
                else:
                    trip_set.append(pi_label[k][stop][-1])
                    stop = pi_label[k][stop][1]
                    k = k - 1
        return trip_set


def post_processing_rraptor_full(DESTINATION, pi_label, PRINT_PARA, label, route_set):
    '''
    Full post processing for rRAPTOR. Currently supported functionality:
        1. Print the output
        2. Routes required for covering pareto-optimal set.
        3. Trips required for covering pareto-optimal set.
    Args:
        DESTINATION: DESTINATION stop id (int)
        pi_label: Nested dict used for backtracking. Primary keys: Round, Secondary keys: stop id format- {round : {stop_id: pointer_label}}
        PRINT_PARA: 1 or 0. 1 means print complete path (int)
        label: Nested dict to maintain label {round : {stop_id: pandas.datetime}}
        route_set: Set to store routes required for covering pareto-optimal label.

    Returns:
        route_set: Set to store routes required for covering pareto-optimal label. format - {int, int...}

    '''
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][DESTINATION] != -1]

    if rounds_inwhich_desti_reached == []:
        if PRINT_PARA == 1:
            print('DESTINATION cannot be reached with given MAX_TRANSFERs')
        route_set = route_set.union(set())
    else:
        rounds_inwhich_desti_reached.reverse()
        pareto_set = []
        trip_set = []
        rap_out = [label[k][DESTINATION] for k in rounds_inwhich_desti_reached]
        for k in rounds_inwhich_desti_reached:
            transfer_needed = k - 1
            journey = []
            stop = DESTINATION
            while pi_label[k][stop] != -1:
                journey.append(pi_label[k][stop])
                mode = pi_label[k][stop][0]
                if mode == 'walking':
                    stop = pi_label[k][stop][1]
                else:
                    trip_set.append(pi_label[k][stop][-1])
                    stop = pi_label[k][stop][1]
                    k = k - 1
            journey.reverse()
            pareto_set.append((transfer_needed, journey))
            if PRINT_PARA == 1:
                _print_Journey_legs(pareto_set)
            for trip in trip_set:
                route_set = route_set.union({int(trip.split("_")[0])})
    return route_set

"""