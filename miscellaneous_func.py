"""
Module contains miscellaneous functions used for reading data, printing logo etc.
"""
import os
import pickle
from random import sample

import networkx as nx
import pandas as pd


def read_testcase(NETWORK_NAME: str) -> tuple:
    """
    Reads the GTFS network and preprocessed dict. If the dicts are not present, dict_builder_functions are called to construct them.

    Args:
        NETWORK_NAME (str): name of the network

    Returns:
        stops_file (pandas.dataframe):  stops.txt file in GTFS.
        trips_file (pandas.dataframe): trips.txt file in GTFS.
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        transfers_file (pandas.dataframe): dataframe with transfers (footpath) details.
        stops_dict (dict): keys: route_id, values: list of stop id in the route_id. Format-> dict[route_id] = [stop_id]
        stoptimes_dict (dict): keys: route ID, values: list of trips in the increasing order of start time. Format-> dict[route_ID] = [trip_1, trip_2] where trip_1 = [(stop id, arrival time), (stop id, arrival time)]
        footpath_dict (dict): keys: from stop_id, values: list of tuples of form (to stop id, footpath duration). Format-> dict[stop_id]=[(stop_id, footpath_duration)]
        route_by_stop_dict_new (dict): keys: stop_id, values: list of routes passing through the stop_id. Format-> dict[stop_id] = [route_id]
        idx_by_route_stop_dict (dict): preprocessed dict. Format {(route id, stop id): stop index in route}.

    Examples:
        >>> NETWORK_NAME = './anaheim'
        >>> read_testcase('NETWORK_NAME')
    """
    import gtfs_loader
    from dict_builder import dict_builder_functions
    stops_file, trips_file, stop_times_file, transfers_file = gtfs_loader.load_all_db(NETWORK_NAME)
    if not os.path.exists(f'./dict_builder/{NETWORK_NAME}/'):
        os.makedirs(f'./dict_builder/{NETWORK_NAME}/')
    try:
        stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = gtfs_loader.load_all_dict(
            NETWORK_NAME)
    except FileNotFoundError:
        print("Building required dictionaries")
        stops_dict = dict_builder_functions.build_save_stops_dict(stop_times_file, trips_file, NETWORK_NAME)
        stoptimes_dict = dict_builder_functions.build_save_stopstimes_dict(stop_times_file, trips_file, NETWORK_NAME)
        routes_by_stop_dict = dict_builder_functions.build_save_route_by_stop(stop_times_file, NETWORK_NAME)
        footpath_dict = dict_builder_functions.build_save_footpath_dict(transfers_file, NETWORK_NAME)
        idx_by_route_stop_dict = dict_builder_functions.build_stop_idx_in_route(stop_times_file, NETWORK_NAME)
        routesindx_by_stop_dict = dict_builder_functions.build_routesindx_by_stop_dict(NETWORK_NAME)
    return stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict


def print_logo() -> None:
    """
    Prints the logo

    Args:
        None

    Returns:
        None

    """
    print("""
****************************************************************************************
*                            TRANSIT ROUTING ALGORITHMS                                 *                       
*           Prateek Agarwal                             Tarun Rambha                    *
*        (prateeka@iisc.ac.in)                     (tarunrambha@iisc.ac.in)             *              
****************************************************************************************
""")
    return None


def print_network_details(transfers_file, trips_file, stops_file) -> None:
    """
    Prints the network details like number of routes, trips, stops, footpath

    Args:
        transfers_file (pandas.dataframe): dataframe with transfers (footpath) details.
        trips_file (pandas.dataframe): dataframe with trip details.
        stops_file (pandas.dataframe): dataframe with stop details.

    Returns:
        None

    """
    print("___________________________Network Details__________________________")
    print("| No. of Routes |  No. of Trips | No. of Stops | No. of Footapths  |")
    print(
        f"|     {len(set(trips_file.route_id))}      |  {len(set(trips_file.trip_id))}        | {len(set(stops_file.stop_id))}        | {len(transfers_file)}             |")
    print("____________________________________________________________________")
    return None


def print_query_parameters(NETWORK_NAME: str, SOURCE: int, DESTINATION, D_TIME, MAX_TRANSFER: int, WALKING_FROM_SOURCE: int, variant: int, no_of_partitions=None, weighting_scheme=None, partitioning_algorithm=None) -> None:
    """
    Prints the input parameters related to the shortest path query

    Args:
        SOURCE (int): stop-id DESTINATION stop
        DESTINATION (int/list): stop-id SOURCE stop. For Onetomany algorithms, this is a list.
        D_TIME (pandas.datetime): Departure time
        MAX_TRANSFER (int): Max transfer limit
        WALKING_FROM_SOURCE (int): 1 or 0. 1 means walking from SOURCE is allowed.
        variant (int): variant of the algorithm. 0 for normal version,
                                                 1 for range version,
                                                 2 for One-To-Many version,
                                                 3 for Hyper version
        no_of_partitions (int): number of partitions network has been divided into
        weighting_scheme (str): which weighing scheme has been used to generate partitions.
        partitioning_algorithm (str): which algorithm has been used to generate partitions.

    Returns:
        None

    Examples:
        >>> overlap = print_query_parameters('anaheim', 36, 52, pd.to_datetime('2022-06-30 06:30:00'), 4, 1, 0, None, None, None)

    """
    print("___________________Query Parameters__________________")
    print(f"Network: {NETWORK_NAME}")
    print(f"SOURCE stop id: {SOURCE}")
    print(f"DESTINATION stop id: {DESTINATION}")
    print(f"Maximum Transfer allowed: {MAX_TRANSFER}")
    print(f"Is walking from SOURCE allowed ?: {WALKING_FROM_SOURCE}")
    if variant == 2 or variant == 1:
        print(f"Earliest departure time: 24 hour (Profile Query)")
    else:
        print(f"Earliest departure time: {D_TIME}")
    if variant == 4:
        print(f"Number of partitions: {no_of_partitions}")
        print(f"Partitioning Algorithm used: {partitioning_algorithm}")
        print(f"Weighing scheme: {weighting_scheme}")
    print("_____________________________________________________")
    return None


def read_partitions(stop_times_file, NETWORK_NAME: str, no_of_partitions: int, weighting_scheme: str, partitioning_algorithm: str) -> tuple:
    """
    Reads the fill-in information.

    Args:
        stop_times_file (pandas.dataframe): dataframe with stoptimes details
        NETWORK_NAME (str): name of the network        no_of_partitions (int): number of partitions network has been divided into.
        weighting_scheme (str): which weighing scheme has been used to generate partitions.
        partitioning_algorithm (str):which algorithm has been used to generate partitions. Currently supported arguments are hmetis or kahypar.

    Returns:
        stop_out (dict) : key: stop-id (int), value: stop-cell id (int). Note: if stop-cell id of -1 denotes cut stop.
        route_groups (dict): key: tuple of all possible combinations of stop cell id, value: set of route ids belonging to the stop cell combination
        cut_trips (set): set of trip ids that are part of fill-in.
        trip_groups (dict): key: tuple of all possible combinations of stop cell id, value: set of trip ids belonging to the stop cell combination
    """
    import itertools
    if partitioning_algorithm == "hmetis":
        route_out = pd.read_csv(f'./partitions/{NETWORK_NAME}/routeout_{weighting_scheme}_{no_of_partitions}.csv',
                                usecols=['path_id', 'group']).groupby('group')
        stop_out = pd.read_csv(f'./partitions/{NETWORK_NAME}/cutstops_{weighting_scheme}_{no_of_partitions}.csv', usecols=['stop_id', 'g_id'])
        fill_ins = pd.read_csv(f'./partitions/{NETWORK_NAME}/fill_ins_{weighting_scheme}_{no_of_partitions}.csv')
    elif partitioning_algorithm == "kahypar":
        route_out = pd.read_csv(f'./kpartitions/{NETWORK_NAME}/routeout_{weighting_scheme}_{no_of_partitions}.csv', usecols=['path_id', 'group']).groupby(
            'group')
        stop_out = pd.read_csv(f'./kpartitions/{NETWORK_NAME}/cutstops_{weighting_scheme}_{no_of_partitions}.csv', usecols=['stop_id', 'g_id']).astype(int)
        fill_ins = pd.read_csv(f'./kpartitions/{NETWORK_NAME}/fill_ins_{weighting_scheme}_{no_of_partitions}.csv')

    fill_ins.fillna(-1, inplace=True)
    fill_ins['routes'] = fill_ins['routes'].astype(int)
    print(f'_________Fill-in information for {len(set(stop_out.g_id)) - 1} Partition_________')
    print(
        f'Number of cutstops: {(len(stop_out[stop_out.g_id == -1]))} ({round((len(stop_out[stop_out.g_id == -1])) / (len(stop_out)) * 100, 2)}%)')
    stop_out = {row.stop_id: row.g_id for _, row in stop_out.iterrows()}
    cut_trips = set(fill_ins['trips'])
    route_partitions, trip_partitions = {}, {}
    for g_id, rotes in route_out:
        route_partitions[g_id] = set((rotes['path_id']))
        trip_partitions[g_id] = set(stop_times_file[stop_times_file.route_id.isin(route_partitions[g_id])].trip_id)
    trip_partitions[-1] = set(fill_ins['trips'])
    grups = list(itertools.combinations(trip_partitions.keys(), 2))
    trip_groups = {}
    for group in grups:
        trip_groups[tuple(sorted(group))] = trip_partitions[group[0]].union(trip_partitions[group[1]]).union(
            trip_partitions[-1])
    for x in trip_partitions.keys():
        trip_groups[(x, x)] = trip_partitions[x].union(trip_partitions[-1])
    route_partitions[-1] = set(fill_ins['routes'])
    route_partitions[-1].remove(-1)
    route_groups = {}
    for group in grups:
        route_groups[tuple(sorted(group))] = route_partitions[group[0]].union(route_partitions[group[1]]).union(
            route_partitions[-1])
    for x in route_partitions.keys():
        route_groups[(x, x)] = route_partitions[x].union(route_partitions[-1])
    print(f"fill-in trips: {len(cut_trips)} ({round(len(cut_trips) / len(set(stop_times_file.trip_id)) * 100, 2)}%)")
    print(
        f'fill-in routes: {len(set(fill_ins.routes)) - 1} ({round((len(set(fill_ins.routes)) - 1) / len(set(stop_times_file.route_id)) * 100, 2)}%)')
    print("____________________________________________________")
    return stop_out, route_groups, cut_trips, trip_groups


def read_nested_partitions(stop_times_file, NETWORK_NAME: str, no_of_partitions: int, weighting_scheme: str) -> tuple:
    """
    Read fill-ins in case of nested partitioning.

    Args:
        stop_times_file (pandas.dataframe): dataframe with stoptimes details
        NETWORK_NAME (str): name of the network        no_of_partitions (int): number of partitions network has been divided into.
        weighting_scheme (str): which weighing scheme has been used to generate partitions.

    Returns:
        stop_out (dict) : key: stop-id (int), value: stop-cell id (int). Note: if stop-cell id of -1 denotes cut stop.
        route_groups (dict): key: tuple of all possible combinations of stop cell id, value: set of route ids belonging to the stop cell combination
        cut_trips (set): set of trip ids that are part of fill-in.
        trip_groups (dict): key: tuple of all possible combinations of stop cell id, value: set of trip ids belonging to the stop cell combination
    """
    import warnings
    from pandas.core.common import SettingWithCopyWarning
    warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
    import itertools
    main_partitions = no_of_partitions
    route_out = pd.read_csv(f'./kpartitions/{NETWORK_NAME}/nested/nested_route_out_{weighting_scheme}_{main_partitions}.csv')
    stop_out = pd.read_csv(f'./kpartitions/{NETWORK_NAME}/nested/nested_cutstops_{weighting_scheme}_{main_partitions}.csv')
    fill_ins = pd.read_csv(f'./kpartitions/{NETWORK_NAME}//nested/nested_fill_ins_{weighting_scheme}_{main_partitions}.csv')
    fill_ins.fillna(-1, inplace=True)
    fill_ins['routes'] = fill_ins['routes'].astype(int)
    temp = stop_out.drop(columns=['lat', 'long', 'boundary_g_id'])
    cut_stops_db = temp[temp.isin([-1]).any(axis=1)]
    #    print(f'Upper Partition: {len(set(stop_out.g_id)) - 1} (2-way nesting)')
    #    print(f'{len(cut_stops_db)} ({round((len(cut_stops_db)) / (len(stop_out)) * 100, 2)} Total cutstops%)')

    start = 0
    normal_stops = stop_out[~stop_out.index.isin(cut_stops_db.index)]
    for x in set(normal_stops.g_id):
        normal_stops.loc[:, f"lower_cut_stops_{x}"] = normal_stops[f"lower_cut_stops_{x}"] + start
        start = start + 2
    stop_out = {row.stop_id: row[f"lower_cut_stops_{row.g_id}"] for _, row in normal_stops.iterrows()}
    stop_out.update({stopp: -1 for stopp in set(cut_stops_db.stop_id)})
    route_partitions, trip_partitions = {}, {}
    route_groups = route_out.groupby('group')
    for g_id, rotes in route_groups:
        route_partitions[g_id] = set((rotes['path_id']))
        trip_partitions[g_id] = set(stop_times_file[stop_times_file.route_id.isin(route_partitions[g_id])].trip_id)
    trip_partitions[-1] = set(fill_ins['trips'])
    grups = list(itertools.combinations(trip_partitions.keys(), 2))
    trip_groups = {}
    for group in grups:
        trip_groups[tuple(sorted(group))] = trip_partitions[group[0]].union(trip_partitions[group[1]]).union(
            trip_partitions[-1])
    for x in trip_partitions.keys():
        trip_groups[(x, x)] = trip_partitions[x].union(trip_partitions[-1])

    route_partitions[-1] = set(fill_ins['routes'])
    route_partitions[-1].remove(-1)
    grups = list(itertools.combinations(route_partitions.keys(), 2))
    route_groups = {}
    for group in grups:
        route_groups[tuple(sorted(group))] = route_partitions[group[0]].union(route_partitions[group[1]]).union(
            route_partitions[-1])
    for x in route_partitions.keys():
        route_groups[(x, x)] = route_partitions[x].union(route_partitions[-1])

    cut_trips = set(fill_ins['trips'])
    return stop_out, route_groups, cut_trips, trip_groups


def check_nonoverlap(stoptimes_dict: dict, stops_dict: dict) -> set:
    '''
    Check for non overlapping trips in stoptimes_dict. If found, it reduces the timestamp of the earlier trip by 1 second.
    This process is repeated until overlapping trips=null. Note 1 second is taken to avoid creation of new overlapping trips
    due to timestamp correction.

    Args:
        stoptimes_dict (dict): preprocessed dict. Format {route_id: [[trip_1], [trip_2]]}.
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.

    Returns:
        overlap (set): set of routes with overlapping trips.

    Examples:
        >>> overlap = check_nonoverlap(stoptimes_dict, stops_dict)

    '''
    for x in stops_dict.items():
        if len(x[1]) != len(set(x[1])):
            print(f'duplicates stops in a route {x}')
    overlap = set()  # Collect routes with non-overlapping trips
    for r_idx, route_trips in stoptimes_dict.items():
        for x in range(len(route_trips) - 1):
            first_trip = route_trips[x]
            second_trip = route_trips[x + 1]
            if any([second_trip[idx][1] <= first_trip[idx][1] for idx, stamp in enumerate(first_trip)]):
                overlap = overlap.union({r_idx})
    if overlap:
        print(f"{len(overlap)} have overlapping trips")
        while overlap:
            for r_idx in overlap:  # Correct routes with non-overlapping trips
                route_trips = stoptimes_dict[r_idx].copy()
                for x in range(len(route_trips) - 1):
                    first_trip = route_trips[x]
                    second_trip = route_trips[x + 1]
                    for idx, _ in enumerate(first_trip):
                        if second_trip[idx][1] <= first_trip[idx][1]:
                            stoptimes_dict[r_idx][x][idx] = (second_trip[idx][0], second_trip[idx][1] - pd.to_timedelta(1, unit="seconds"))
            overlap = set()  # Collect (again) routes with non-overlapping trips
            for r_idx, route_trips in stoptimes_dict.items():
                for x in range(len(route_trips) - 1):
                    first_trip = route_trips[x]
                    second_trip = route_trips[x + 1]
                    if any([second_trip[idx][1] <= first_trip[idx][1] for idx, stamp in enumerate(first_trip)]):
                        overlap = overlap.union({r_idx})
            if overlap:
                print(f"{len(overlap)} have overlapping trips")
    return overlap


def get_full_trans(NETWORK_NAME: str, time_limit) -> None:
    '''
    Make the footpath graph transitively close and saves it in the form of transfer_dict
    Note: time_limit="full" means consider all footpaths

    Args:
        NETWORK_NAME (str): Network NETWORK_NAME
        time_limit (str/int): maximum footpath duration to be considered (before footpath graph is made transitively closed)

    Returns:
        None

    Examples:
        >>> get_full_trans('anaheim', 180)
    '''
    #    print('editing transfers')
    transfers_file = pd.read_csv(f'Data/GTFS/{NETWORK_NAME[2:]}/transfers.txt', sep=',')
    ini_len = len(transfers_file)
    # print(f"initial graph transfer {len(transfers_file)}")
    if time_limit != "full":
        transfers_file = transfers_file[transfers_file.min_transfer_time < time_limit].reset_index(drop=True)
    G = nx.Graph()
    edges = list(zip(transfers_file.from_stop_id, transfers_file.to_stop_id, transfers_file.min_transfer_time))
    G.add_weighted_edges_from(edges)
    connected = [c for c in nx.connected_components(G)]
    for tree in connected:
        for SOURCE in tree:
            for desti in tree:
                if SOURCE != desti and (SOURCE, desti) not in G.edges():
                    G.add_edge(SOURCE, desti, weight=nx.dijkstra_path_length(G, SOURCE, desti))
    footpath = list(G.edges(data=True))
    reve_edges = [(x[1], x[0], x[-1]) for x in G.edges(data=True)]
    footpath.extend(reve_edges)
    footpath_db = pd.DataFrame(footpath)
    footpath_db[2] = footpath_db[2].apply(lambda x: list(x.values())[0])
    footpath_db.rename(columns={0: "from_stop_id", 1: "to_stop_id", 2: "min_transfer_time"}, inplace=True)
    footpath_db.to_csv(f'./GTFS/{NETWORK_NAME}/transfers_full.csv', index=False)
    if len(footpath_db) != ini_len:
        print(f"initial graph transfer {len(transfers_file)}")
        print(f"full graph transfer {len(footpath_db)}")
        print(f"check")
    transfers_dict = {}
    g = footpath_db.groupby("from_stop_id")
    for from_stop, details in g:
        transfers_dict[from_stop] = []
        for _, row in details.iterrows():
            transfers_dict[from_stop].append(
                (row.to_stop_id, pd.to_timedelta(float(row.min_transfer_time), unit='seconds')))
    with open(f'./dict_builder/{NETWORK_NAME}/transfers_dict_full.pkl', 'wb') as pickle_file:
        pickle.dump(transfers_dict, pickle_file)
    return None


def check_footpath(footpath_dict: dict) -> None:
    '''
    Check if the footpaths are transitively close. Prints error if not.

    Args:
        footpath_dict: Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}

    Returns:
        None

    Examples:
        >>> check_footpath(footpath_dict)
    '''
    edges = []
    for from_s, to_s in footpath_dict.items():
        to_s, _ = zip(*to_s)
        edges.extend([(from_s, x) for x in to_s])
    G = nx.Graph()
    G.add_edges_from(edges)
    connected = [c for c in nx.connected_components(G)]
    for connected_comp in connected:
        for SOURCE in connected_comp:
            for desti in connected_comp:
                if SOURCE == desti: continue
                if (SOURCE, desti) not in G.edges():
                    print(SOURCE, desti)
                    raise Exception("Transitive Error in footpath dict")
    return None


def get_random_od(routes_by_stop_dict: dict, NETWORK_NAME: str) -> None:
    """
    Generate Random OD pairs.

    Args:
        routes_by_stop_dict (dict): preprocessed dict. Format {stop_id: [id of routes passing through stop]}.
        NETWORK_NAME (str): Network NETWORK_NAME

    Returns:
        None

    Examples:
        >>> get_random_od(routes_by_stop_dict, 'anaheim')

    """
    random_od_db = pd.DataFrame(columns=["SOURCE", "DESTINATION"])
    desired_len = 100000
    stop_list = list(routes_by_stop_dict.keys())
    while len(random_od_db) < desired_len:
        temp = pd.DataFrame(set(zip(sample(stop_list, 5000), sample(stop_list, 5000))),
                            columns=["SOURCE", "DESTINATION"])
        random_od_db = random_od_db.append(temp, ignore_index=True).drop_duplicates()
        random_od_db = random_od_db[random_od_db['SOURCE'] != random_od_db['DESTINATION']].reset_index(drop=True)
    random_od_db.iloc[:desired_len].to_csv(f"./GTFS/{NETWORK_NAME[2:]}_randomOD.csv", index=False)
    print(f"{NETWORK_NAME} random OD saved")
    return None

def load_TE_graph(NETWORK_NAME: str, stop_times_file)-> tuple:
    """
    Loads the Time expanded Graph

    Args:
        NETWORK_NAME (str): name of the network
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.

    Returns:
        G: NetworkX graph object. Time exapnded graph
        stops_group: pandas.groupby object.
        stopevent_mapping (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Examples:
        >>> G, stops_group, stopevent_mapping = load_TE_graph('anaheim', stop_times_file)

    """
    try:
        with open(f"./Data/time_expanded/graph_{NETWORK_NAME[2:]}", 'rb') as file:
            G = pickle.load(file)
        stops_group = stop_times_file.groupby('stop_id')
        temp = stop_times_file[['stop_id', 'arrival_time']].drop_duplicates().reset_index(drop=True)
        stopevent_mapping = {x[1]: x[0] for x in enumerate(list(zip(temp['stop_id'], temp['arrival_time'])), 1)}

        return G, stops_group, stopevent_mapping
    except FileNotFoundError:
        print("Time expanded files missing")


def load_CSA(NETWORK_NAME: str):
    """
    Loads the connection list for CSA

    Args:
        NETWORK_NAME (str): name of the network

    Returns:
        connections_list (list): list of tuples. format: [(from stop, to stop, from time, to time, trip id)].

    Examples:
        >>> connections_list = load_CSA('anaheim')
    """
    try:
        with open(f'./Data/CSA/{NETWORK_NAME}/connections_list_pkl.pkl', 'rb') as file:
            connections_list = pickle.load(file)
        return connections_list
    except FileNotFoundError:
        print("CSA preprocessing missing")

def load_TBTR(NETWORK_NAME: str)-> tuple:
    """
    Loads the trip-transfer dict for TBTR

    Args:
        NETWORK_NAME (str): name of the network

    Returns:
        trip_transfer_dict (nested dict): keys: id of trip we are transferring from, value: {stop number: list of tuples
        trip_set (set): set of trip ids from which trip-transfers are available.

    Examples:
        >>> trip_transfer_dict, trip_set = load_TBTR('anaheim')

    """
    try:
        with open(f'./Data/TBTR/{NETWORK_NAME}/TBTR_trip_transfer_dict.pkl', 'rb') as file:
            trip_transfer_dict = pickle.load(file)
        trip_set = set(trip_transfer_dict.keys())
        return trip_transfer_dict, trip_set
    except FileNotFoundError:
        print("TBTR preprocessing missing")
