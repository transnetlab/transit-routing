from collections import deque as deque

import pandas as pd


################################################################################################################################################################################################
def build_odpair_from_etm():
    """
    Using ETM data of oct month, collect all to and from stops. Shuffle them and return a list of od-pairs
    """
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
    bus_stop = pd.read_csv(
        "D:/prateek/research/indivisual/BGTFS/raw_data/OneDrive_2020-03-14/Data Documentation/latest data/bus_stop.csv",
        usecols=['bus_stop_id', "bus_stop_name"])
    print(bus_stop[bus_stop["bus_stop_id"] == id]["bus_stop_name"])


def initlize(routes_by_stop_dict, source, transfer):
    """
    Initlizes labels for Raptor. Inf_time means is a paramter used to signify infinite time. (It's value is set as current date+365days)
    All labels are stored as dicts are stored according to round/transfer.
    Format of Labels and Pilabels -->dict[round][stop] and starlabel-->dict[stop]
    :param stops: Bus_stop database
    :param source: Bus_stop Id of source
    :param transfer: Max No of transfers
    :param d_time: Departure time
    :return: deque: marked_stop, Dicts : label,pi_label,star_label and varible:inf_time
    """
    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)

    pi_label = {x: {stop: -1 for stop in routes_by_stop_dict.keys()} for x in range(0, transfer + 1)}
    label = {x: {stop: inf_time for stop in routes_by_stop_dict.keys()} for x in range(0, transfer + 1)}
    star_label = {stop: inf_time for stop in routes_by_stop_dict.keys()}

    marked_stop = deque()
    marked_stop.append(source)
    return (marked_stop, label, pi_label, star_label, inf_time)


################################################################################################################################################################################################
# Call:check_stop_validity(1,2)
def check_stop_validity(stops, source, destination):
    """
    Checks if the source are destination entered are correct or not. This is because stop sequence is not continuous.
    :param stops:Bus_stops database
    :param source: Bus_stop Id of source
    :param destination: BUs_stop if of destination
    """
    if source in stops.stop_id and destination in stops.stop_id:
        print('correct inputs')
    else:
        print("incorrect inputs")


##################################################################################################################################################################################################
# N##ote3:A route(stops 1 to 20) may contain 2 trip pattern with trip 1 from 1 to 10 and trip 2  from 10 to 20.  I want earliest trip from 10 after 11pm. Now Trip 1
# may end at 10 at 12pm thus stop 10 has time stamp greater than 10 but I cannot hop on this trip from stop 10. Technically this is coz  we should use dep_time
# for finding trip and for such a case dep_time would not be defined for ending station. For now dep_time is populated same is arrival time everywhere. Trip[:1] skips
# the last element and thus takes care of this
# Note:(Not Correct now i gues.. coz on one route bus might not be defined but it might be on other routes.) get_latest_trip may produce error 'local variable 'current_trip' referenced before assignment' coz if the source stop is  2 then  there is no bus from it after 9AM.
# Thus, it may cause error if the deaprting time is after 9Am at stop 2. To avoid it, intilize the departing time early like 6 Am. This
# Also. from stop zero there first bus is at 6AM. If the departing time is 5Am , that is taken care of(meaning itll give earliest trip at that stop as that of 6 Am)
####Call:get_latest_trip(route,p_i,d_time_at_pi)
# d_time_at_pi=previous_arrival_at_pi
# stoptimes_dict[22543][0]
def get_latest_trip_new(stoptimes_dict, route, arrival_time_at_pi, pi_index, change_time):
    # stoptimes_dict, route, p_i, arrival_time_at_pi, pi_index = stoptimes_dict, route, p_i, previous_arrival_at_pi,stopindex_by_route
    try:
        for trip_idx, trip in enumerate(stoptimes_dict[route]):
            if trip[pi_index][1] >= arrival_time_at_pi + change_time:
                return f'{route}_{trip_idx}', stoptimes_dict[route][trip_idx]
        return -1, -1  # No trip is found after arrival_time_at_pi
    except KeyError:
        return -1, -1  # NO trip exsist for this route. in this case check tripid from trip file for this route and then look waybill.ID. Likely that trip is across days thats why it is rejected in stoptimes builder while checking


#####################################################################################################################################################################################################################
# NOTE:Not all stops have tranfers. In delhi, with current specs, 1 does not have
##CALL: get_transfers(2)
def footpath_connections(footpath_dict, from_stop):
    """
    For a given stop, find all Footpath connections available from it.
    :param transfers_dict:dict containing footpaths
    :param from_stop: bus stop id of from_stop
    :return:list:[(destination,walking_time)]
    """
    footpaths = []
    if from_stop in footpath_dict.keys():
        for to_pair in footpath_dict[from_stop]:
            to_stop = to_pair[0]
            timee = pd.to_timedelta(to_pair[1], unit='seconds')
            footpaths.append((to_stop, timee))
    return (footpaths)


###########################################################################################################################################################################################################################################
# call: p_i_in_current_trip(current_trip_t,5374)
def p_i_in_current_trip(trip, p_i):
    """
    Checks if a stop p is in the current trip or not
    :param trip: trip in the form of list
    :param p_i:  bus_stop id of stop p_i
    :return: True/False
#Olderfunction
    default = False
    for x in trip:
        if x[0] == p_i:
            default = True
            break
    return (default)
    """
    for x in trip:
        if x[0] == p_i:
            return True
    return False


################################################################################################################################################################################################################################################################
# p_i_is_last_stop_for_currentTrip(trip,554)
def p_i_is_last_stop_for_currentTrip(trip, p_i):
    """
    Checks if the stop p_i is the last stop of the current trip or not
    :param trip: trip in the form of list
    :param p_i:  bus_stop id of stop p_i
    :return: True/False
    """
    if trip[-1][0] == p_i:
        return True
    else:
        return False


################################################################################################################################################################################################################################################################
def print_Journey_legs(pareto_journeys):
    # print(f'final Journey is \n {journey}')
    for _, journey in pareto_journeys:
        for leg in journey:
            if leg[0] == 'walking':
                print(f'from {leg[1]} walk uptil  {leg[2]} for {leg[3]} minutes and reach at {leg[4].time()}')
            else:
                print(
                    f'from {leg[1]} board at {leg[0].time()} and get down on {leg[2]} at {leg[3].time()} along {leg[-1]}')
        print("####################################")


###########################################################################################################################################################################################################################################
def draw_output(journey_list):
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


###########################################################################################################################################################################################################################################
# USED/FOR DELHI/TO BE USED FUNCTIONS
###########################################################################################################################################################################################################################################
'''
        for x in range(len(stoptimes_dict[route][x]):
        while p_i=
    current_trip={}
#    jump=len(stops_dict[route])
    count=len(stoptimes_dict[route])
    for x in range(len(stoptimes_dict[route])):
        start_time = dt.datetime.strptime(stoptimes_dict[route][x][0], '%H:%M:%S')
        if start_time>d_time:
            current_trip['current_trip'] = stoptimes_dict[route][x]
            current_trip['trip_index'] = x
            return(current_trip)
        else:print('no trip found')
    mid_time = dt.datetime.strptime(stoptimes_dict[route][count//2][0], '%H:%M:%S')
    if d_time<mid_time:
        for x in range(0, count//2):
            checking_trip=dt.datetime.strptime(stoptimes_dict[route][x][0], '%H:%M:%S')
            if checking_trip < d_time:
                continue
            else:
                current_trip['current_trip']=stoptimes_dict[route][x]
                current_trip['trip_index'] = x
                break
        return (current_trip)
    else:
        for x in range(count//2, count):
            checking_trip=dt.datetime.strptime(stoptimes_dict[route][x][0], '%H:%M:%S')
            if checking_trip < d_time:
                continue
            else:
                current_trip['current_trip']=stoptimes_dict[route][x]
                current_trip['trip_index']=x
                break
        return (current_trip)
'''
##############################################################################################################################
'''
def wait_time():
    wait_time={}
    define_time=dt.datetime.strptime('00:03:00', '%H:%M:%S')
    for x in stops.stop_id:
        wait_time[x]=define_time
    return wait_time
'''
##############################################################################################################################
'''
def routes_by_stop(stop_p):
    routes_serving_p=[]
    for route_r in stops_dict.keys():
        for stops_in_r in stops_dict[route_r]:
            if stops_in_r==stop_p:
                routes_serving_p.append(route_r)
                break
    return(routes_serving_p)
'''
##############################################################################################################################
'''Old FUNCTIN WHICH READS FROM TRANSFERS DB> NEW ONE READS FROM DICt
def get_transferss(stop):
    tran_info=[]
    for x in range(0,len(transfers)):
        if transfers.from_stop_id.iloc[x]==stop:
            timee=dt.timedelta(seconds=float(transfers.min_transfer_time.iloc[x]))
#            tt=time.strftime('%H:%M:%S', time.gmtime(transfers.iloc[x][3]))
#            timee=dt.datetime.strptime(tt, '%H:%M:%S')
            tran_info.append((transfers.iloc[x][1],timee))
    return (tran_info)
'''


##############################################################################################################################
def update_record(source, destination, pareto_set, d_time, output_list):
    j = []
    for trnsfer, journey in pareto_set:
        temp = {}
        temp["source"] = source
        temp["desti"] = destination
        temp["query_time"] = d_time.time()
        temp["departure_time"] = journey[0][0].time()
        total_time = calculate_tt(journey)
        temp["TT"] = total_time
        temp["wait_time"] = waiting_time(journey, d_time)
        temp["transfer"] = trnsfer
        temp["IVTT"] = 0
        temp["OVTT"] = 0
        IVTT_time = calcuLATE_ivtt(journey)
        temp["IVTT"] = IVTT_time
        temp["OVTT"] = total_time - IVTT_time
        j.append(temp)
    output_list.extend(j)


#        temp["details"] = journey
def calculate_tt(journey):
    return round((pd.to_timedelta(journey[-1][-1] - journey[0][0])).total_seconds() / 60, 2)


def waiting_time(journey, d_time):
    return round((pd.to_timedelta(journey[0][0] - d_time)).total_seconds() / 60, 2)


def calcuLATE_ivtt(journey):
    IVTT = 0
    for leg in range(len(journey)):
        if type(journey[leg][0]) != str:
            IVTT = IVTT + (journey[leg][3] - journey[leg][0]).total_seconds()
    return round(IVTT / 60, 2)


def check(stops_dict, stoptimes_dict, stop_times_file):
    """
    Do not check route stops wrt route point file as somestops have been deleted while building these dict
    """
    if not stops_dict.keys() == stoptimes_dict.keys():
        print(f"route are different in stopsdict and stoptimes dict")
    for stopdict_r_id, stopdict_r_stops in stops_dict.items():
        trips = stoptimes_dict[stopdict_r_id]
        for temp_index in range(len(trips)):
            stoptime_stops, stoptime_times = list(zip(*trips[temp_index]))
            if not list(stoptime_stops) == stopdict_r_stops:
                print(f"stops seq differ in stoptimes and stop dict for id {stopdict_r_id}")
            for stamps in range(len(stoptime_times) - 1):
                if not stoptime_times[stamps + 1] >= stoptime_times[stamps]:
                    print(f"timestamps seq error in stoptimes {stopdict_r_id} for tripid {temp_index}")
    print(f"stop_dict and stoptimes_dict check complete")


def post_processing(destination, pi_label, print_para, label, save_routes, routes_exp):
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][destination] != -1]

    if rounds_inwhich_desti_reached == []:
        if print_para == 1:
            print('Destination cannot be reached with given max_transfers')
        return -1, -1, -1
    else:
        rounds_inwhich_desti_reached.reverse()
        pareto_set = []
        trip_set = []
        rap_out = [label[k][destination] for k in rounds_inwhich_desti_reached]
        for k in rounds_inwhich_desti_reached:
            transfer_needed = k - 1
            journey = []
            stop = destination
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

        if print_para == 1:
            print_Journey_legs(pareto_set)
        save_routesExplored(save_routes, routes_exp)
        return rounds_inwhich_desti_reached, trip_set, rap_out


def save_routesExplored(save_routes, routes_exp):
    if save_routes == 1:
        temp = []
        for x in routes_exp.items():
            temp.extend(list(zip([x[0] for y in x[1]], x[1])))
        pd.DataFrame(temp, columns=['round', 'route']).to_csv(r'./routes_exp_orig.csv', index=False)


def post_processing_rraptor_partial(destination, pi_label):
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][destination] != -1]

    if rounds_inwhich_desti_reached == []:
        return []
    else:
        rounds_inwhich_desti_reached.reverse()
        trip_set = []
        for k in rounds_inwhich_desti_reached:
            stop = destination
            while pi_label[k][stop] != -1:
                mode = pi_label[k][stop][0]
                if mode == 'walking':
                    stop = pi_label[k][stop][1]
                else:
                    trip_set.append(pi_label[k][stop][-1])
                    stop = pi_label[k][stop][1]
                    k = k - 1
        return trip_set


def post_processing_rraptor_full(destination, pi_label, print_para, label, route_set):
    rounds_inwhich_desti_reached = [x for x in pi_label.keys() if pi_label[x][destination] != -1]

    if rounds_inwhich_desti_reached == []:
        if print_para == 1:
            print('Destination cannot be reached with given max_transfers')
        route_set = route_set.union(set())
    else:
        rounds_inwhich_desti_reached.reverse()
        pareto_set = []
        trip_set = []
        rap_out = [label[k][destination] for k in rounds_inwhich_desti_reached]
        for k in rounds_inwhich_desti_reached:
            transfer_needed = k - 1
            journey = []
            stop = destination
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
            if print_para == 1:
                print_Journey_legs(pareto_set)
            for trip in trip_set:
                route_set = route_set.union({int(trip.split("_")[0])})
    return route_set
'''
def get_latest_trip_new(stoptimes_dict, route, arrival_time_at_pi, pi_index, change_time):
    # stoptimes_dict, route, p_i, arrival_time_at_pi, pi_index = stoptimes_dict, route, p_i, previous_arrival_at_pi,stopindex_by_route
    try:
        for trip_idx in range(len(stoptimes_dict[route])):
            if stoptimes_dict[route][trip_idx][pi_index][1] >= arrival_time_at_pi + change_time:
                return f'{route}_{trip_idx}', stoptimes_dict[route][trip_idx]
        else:
            return -1, -1  # No trip is found after arrival_time_at_pi
    except KeyError:
        return -1, -1  # NO trip exsist for this route. in this case check tripid from trip file for this route and then look waybill.ID. Likely that trip is across days thats why it is rejected in stoptimes builder while checking
#####################################################################################################################################################################################################
# Call:routes_by_stop(stop_p)

def routes_by_stop(stops_dict, stop_p):
    """
    Fetches all routes passing from from a given stop p. Here I am assuming that route a one-way.
    Note:lets say I want all routes serving stop 20 and there is a route- 500 such its stops are 1-20.
    Since it is ending at 20, there is no point in considering it.
    :param stops_dict:
    :param stop_p: Bus_stop id of stop p
    :return: list:routes_serving_p
    """
    #    stop_p=8456
    routes_serving_p = []
    for route in stops_dict.keys():
        if stop_p in stops_dict[route][:-1]:
            routes_serving_p.append(route)
    return routes_serving_p



######################################################################################################################################################################################################################
# intilizes change time for all stops as 1 min. Gives a dictnary with key as stops and value as ch.time=1 min for all
def ch_time(routes_by_stop_dict):
    """
    Here for each stop, we initlize change time. Value used here is 1 min for all stops
    Returns a dict of format-->dict[stop]
    :param stops: bus_stop database
    :return: dict:change time
    """
    change_time = {}
    define_time = pd.to_timedelta(10, unit='seconds')
    for x in routes_by_stop_dict.keys():
        change_time[x] = define_time
    return change_time
#################################################################################################################################################################################################################
# call arr_by_t_at_pi(current_trip_t,p_i)

def arri_by_t_at_pi(trip, p_i):
    """
    Returns arrival time of a trip at stop p_i
    :param trip: trip in the form of list
    :param p_i: bus_stop id of stop p_i
    :return: arrival time at p_i
    """
    #    trip=current_trip_t
    for x in trip:
        if x[0] == p_i:
            time = x[1]
            return time



'''
