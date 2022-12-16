"""
Builds data structure for TBTR related algorithms
"""
from itertools import chain
import os
import multiprocessing
from random import shuffle
from time import time as time_measure
# print(os.getcwd())
# os.chdir(os.path.dirname(os.getcwd()))
# os.chdir('D:\\prateek\\research\\indivisual\\TB2')
from collections import defaultdict
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
import sys
import gtfs_loader
from miscellaneous_func import *


def algorithm1_parallel(route_details: tuple) -> list:
    """
    Collects all possible trip transfers.

    Args:
        route_details (list): tuple of format: (route id, list of trips)

    Returns:
        list of trip-transfers  format [(from trip id, from stop id, to strip id, to stop id)]
    """
    trip_transfer_list = []
    rr, route_trips = route_details
    for tcount, trips in enumerate(route_trips):
        for scount, stop_seq in enumerate(trips[1:], 1):
            try:
                to_route_list = routes_by_stop_dict[stop_seq[0]].copy()
                to_route_list.remove(rr)
                for r_route in to_route_list:
                    stopindex_by_route = stops_dict[r_route].index(stop_seq[0])
                    earliest_trip = -1
                    for ttcount, tripss in enumerate(stoptimes_dict[r_route]):
                        if tripss[stopindex_by_route][1] >= change_time + stop_seq[1]:
                            earliest_trip = 1
                            break
                    if earliest_trip == 1:
                        if r_route != rr or tcount < ttcount or stopindex_by_route < scount:
                            trip_transfer_list.append(
                                (f"{rr}_{tcount}", scount, f"{r_route}_{ttcount}", stopindex_by_route))
            except KeyError:
                pass
            try:
                for connection in footpath_dict[stop_seq[0]]:
                    to_route_list = routes_by_stop_dict[connection[0]]
                    for r_route in to_route_list:
                        stopindex_by_route = stops_dict[r_route].index(connection[0])
                        earliest_trip = -1
                        for ttcount, tripss in enumerate(stoptimes_dict[r_route]):
                            if tripss[stopindex_by_route][1] >= stop_seq[1] + connection[1]:
                                earliest_trip = 1
                                break
                        if earliest_trip == 1:
                            if r_route != rr or tcount < ttcount or stopindex_by_route < scount:
                                trip_transfer_list.append(
                                    (f"{rr}_{tcount}", scount, f"{r_route}_{ttcount}", stopindex_by_route))
            except KeyError:
                pass
    return trip_transfer_list


def algorithm2_parallel(trip_transfer_: list) :
    """
    Removes trip transfers which cause U-turns.

    Args:
        trip_transfer_ (list): trip transfers. Format : ['index', 'from_routeid', 'from_tid', 'to_routeid', 'to_tid', 'from_stop_index', 'to_stop_index']

    Returns:
        Returns the index if the trip-transfer is optimal. Else empty list

    """
    try:
        from_stop_dep, to_stop_det = stoptimes_dict[trip_transfer_[1]][trip_transfer_[2]][trip_transfer_[5]], \
                     stoptimes_dict[trip_transfer_[3]][trip_transfer_[4]][trip_transfer_[6]]
        if from_stop_dep[0] == to_stop_det[0] and from_stop_dep[0] <= to_stop_det[0]:
            return trip_transfer_[0]
        else:
            return []
    except IndexError:
        return []


def algorithm3_parallel(trip_details: tuple)-> list:
    """
    Removes trip transfers that are not part of any optimal journey

    Args:
        trip_details: tuple of form: (route_id, trip_id, trip)

    Returns:
        list of non-optimal trip transfers.

    """
    r_id, t_id, trip = trip_details
    removed_trans = []
    stop_labels = defaultdict(lambda: inf_time)
    trip_rev = reversed(list(enumerate(trip)))
    tid = f"{r_id}_{t_id}"
    for s_idx, stop_seq in trip_rev:
        stop_labels[stop_seq[0]] = min(stop_labels[stop_seq[0]], stop_seq[1])
        try:
            for q in footpath_dict[stop_seq[0]]:
                stop_labels[q[0]] = min(stop_labels[q[0]], stop_seq[1] + q[1])
        except KeyError:
            pass
        try:
            trans_from_stop = [(trans, [int(x) for x in trans[1].split("_")]) for trans in trip_transfer_dict[tid] if trans[0] == s_idx]
            for trans, breakdown in trans_from_stop:
                keep = False
                for stop_connect_0, stop_connect_1 in stoptimes_dict[breakdown[0]][breakdown[1]][trans[2] + 1:]:
                    if stop_connect_1 < stop_labels[stop_connect_0]:
                        keep = True
                        stop_labels[stop_connect_0] = stop_connect_1
                    if stop_connect_0 in footpath_keys:
                        for footpath_connect in footpath_dict[stop_connect_0]:
                            if stop_labels[footpath_connect[0]] > stop_connect_1 + footpath_connect[1]:
                                keep = True
                                stop_labels[footpath_connect[0]] = stop_connect_1 + footpath_connect[1]
                if not keep:
                    removed_trans.append((tid, trans))
        except KeyError:
            pass
    return removed_trans

def take_inputs() -> tuple:
    '''
    Takes the required inputs for building TBTR preprocessing
    '''
    breaker = "________________________________"
    print("Building trip-transfers dict for TBTR. Enter following parameters.\n ")
    CORES = int(input(
        f"trip-transfers can be build in parallel. Enter number of CORES (1 for serial). \nAvailable CORES (logical and physical):  {multiprocessing.cpu_count()}\n: "))
    change_time = pd.to_timedelta(0, unit='seconds')
    GENERATE_LOGFILE = int(input(f"Press 1 to redirect output to a log file in logs folder. Else press 0\n: "))
    return breaker, CORES, change_time, GENERATE_LOGFILE


if __name__ == "__main__":
    with open(f'parameters_entered.txt', 'rb') as file:
        parameter_files = pickle.load(file)
    BUILD_TRANSFER, NETWORK_NAME, BUILD_TBTR_FILES = parameter_files
    if BUILD_TBTR_FILES==1:
        # NETWORK_NAME = 'uk'
        # NETWORK_NAME = 'germany'
        breaker, CORES, change_time, GENERATE_LOGFILE = take_inputs()
        print(breaker)
        stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict = read_testcase(
            NETWORK_NAME)
        # inf_time = pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")
        # GENERATE_LOGFILE = 1
        if GENERATE_LOGFILE == 1:
            if not os.path.exists(f'./logs/.'):
                os.makedirs(f'./logs/.')
            sys.stdout = open(f'./logs/tbtr_builder_{NETWORK_NAME}', 'w')
        print(f"Network: {NETWORK_NAME}")
        print(f'CORES used ={CORES}')
        print(breaker)
        ########Algorithm 1
        print("Running Algorithm 1")
        route_details = list(stoptimes_dict.items())
        shuffle(route_details)
        start = time_measure()
        with Pool(CORES) as pool:
            result = pool.map(algorithm1_parallel, route_details)
        A1_time = time_measure() - start
        Transfer_set_db = pd.DataFrame(list(chain(*result)), columns=["from_Trip", "from_stop_index", "to_trip", "to_stop_index"])
        print(breaker)
        ########Algorithm 2
        print("Running Algorithm 2")
        Transfer_set_db_temp = Transfer_set_db.reset_index()
        Transfer_set_db_temp['from_routeid'], Transfer_set_db_temp['from_tid'] = zip(*Transfer_set_db_temp['from_Trip'].apply(lambda x: x.split("_")))
        Transfer_set_db_temp['to_routeid'], Transfer_set_db_temp['to_tid'] = zip(*Transfer_set_db_temp['to_trip'].apply(lambda x: x.split("_")))
        Transfer_set_db_temp = Transfer_set_db_temp.drop(columns=['from_Trip', 'to_trip']).astype(int)
        Transfer_set_db_temp.from_stop_index = Transfer_set_db_temp.from_stop_index - 1
        Transfer_set_db_temp.to_stop_index = Transfer_set_db_temp.to_stop_index + 1
        Transfer_set_db_temp = Transfer_set_db_temp[['index', 'from_routeid', 'from_tid', 'to_routeid', 'to_tid', 'from_stop_index', 'to_stop_index']]
        start = time_measure()
        with Pool(CORES) as pool:
            U_Turns_list = pool.map(algorithm2_parallel, Transfer_set_db_temp.values.tolist())
        A2_time = time_measure() - start
        U_Turns_list = [x for x in U_Turns_list if x]
        Transfer_set = Transfer_set_db.drop(U_Turns_list).reset_index(drop=True)
        from_T_group = Transfer_set.groupby(['from_Trip'])
        trip_transfer_dict = {idx: list(zip(rows["from_stop_index"], rows['to_trip'], rows['to_stop_index'])) for idx, rows in from_T_group}
        print(breaker)
        ########Algorithm 3
        print("Running Algorithm 3")
        for stop, flist in footpath_dict.items():
            temp = []
            footpath_dict[stop] = [(y[0], y[1].total_seconds()) for y in flist]
        for rid, route_det in stoptimes_dict.items():
            temp = []
            for trip in route_det:
                temp.append([(stamp[0], stamp[1].timestamp()) for stamp in trip])
            stoptimes_dict[rid] = temp
        inf_time = (pd.to_datetime("today").round(freq='H') + pd.to_timedelta("365 day")).timestamp()
        footpath_keys = set(footpath_dict.keys())
        route_details1 = list(stoptimes_dict.items())
        route_details1.sort(key=lambda x: x[0])
        trip_list = []
        for rid, route_trips in route_details1:
            for t_id, trip in enumerate(route_trips):
                trip_list.append((rid, t_id, trip))
        route_details1 = None

        init_tans = sum([len(x) for x in trip_transfer_dict.values()])
        start = time_measure()
        with Pool(CORES) as pool:
            non_optimal_trans = pool.map(algorithm3_parallel, trip_list)
        A3_time = time_measure() - start
        for route_level_turns in non_optimal_trans:
            for tid, trans in route_level_turns:
                trip_transfer_dict[tid].remove(trans)
        final_trans = sum([len(x) for x in trip_transfer_dict.values()])
        print(breaker)
        print(f"Algorithm 1 time - {round(A1_time, 2)},Triptransfer count = {len(Transfer_set_db)}")
        print(
            f"Algorithm 2 time - {round(A2_time, 2)},Triptransfer count = {init_tans} (Reduction: {int(((len(Transfer_set_db) - init_tans) / len(Transfer_set_db)) * 100)})")
        print(f"Algorithm 3 time - {round(A3_time, 2)},Triptransfer count = {final_trans} (Reduction: {int(((init_tans - final_trans) / init_tans) * 100)})")
        print(f"Total time - {round(A1_time + A2_time + A3_time, 1)}")
        print(f"Total time - {round((A1_time + A2_time + A3_time) * CORES, 1)}")
        print(breaker)
        trip_transfer_dict_new = {}
        for tid, connections in trip_transfer_dict.items():
            if connections == []: continue
            trip_transfer_dict_new[tid] = {}
            for x in connections:
                if x[0] not in trip_transfer_dict_new[tid].keys():
                    trip_transfer_dict_new[tid][x[0]] = []
                trip_transfer_dict_new[tid][x[0]].append((x[1], x[2]))
        #Added [] for every stop of key (or cast it as default dict to avoid error keyerror in TBTR code)
        for tid in trip_transfer_dict_new.keys():
            numberofstops = set(range(len(stops_dict[int(tid.split('_')[0])])))
            keys_present = set(trip_transfer_dict_new[tid].keys())
            keystobeadded = numberofstops - keys_present
            for key in keystobeadded:
                trip_transfer_dict_new[tid][key] = []

        with open(f'./GTFS/{NETWORK_NAME}/TBTR_trip_transfer_dict.pkl', 'wb') as pickle_file:
            pickle.dump(trip_transfer_dict_new, pickle_file)
        print("trip_Transfer_dict done final")
        if GENERATE_LOGFILE == 1: sys.stdout.close()

        """
        def remove_Uturns(stop_times_file, change_time, Transfer_set_db):
            U_turns = Transfer_set_db.reset_index()
            U_turns.from_stop_index = U_turns.from_stop_index - 1
            U_turns.to_stop_index = U_turns.to_stop_index + 1
            stop_times_file = stop_times_file[['stop_sequence', 'arrival_time', 'stop_id', 'trip_id']]
        
            U_turns = pd.merge(U_turns, stop_times_file, left_on=['from_Trip', 'from_stop_index'],
                               right_on=['trip_id', 'stop_sequence']). \
                drop(columns=['trip_id', 'stop_sequence']).rename(
                columns={'stop_id': 'from_stop_id', 'arrival_time': 'from_stop_time'})
            U_turns = pd.merge(U_turns, stop_times_file, left_on=['to_trip', 'to_stop_index'],
                               right_on=['trip_id', 'stop_sequence']). \
                drop(columns=['trip_id', 'stop_sequence']).rename(
                columns={'stop_id': 'to_stop_id', 'arrival_time': 'to_stop_time'})
            ch_time = pd.to_timedelta(change_time, unit="seconds")
            U_Turns_list = U_turns[(U_turns.from_stop_id == U_turns.to_stop_id) & (U_turns.from_stop_time + ch_time <= U_turns.to_stop_time)]['index'].to_list()
            return U_Turns_list    
        
        def parallel_algo1(route_details):
        trip_transfer_list = []
        rr, route_trips = route_details
        for tcount, trips in enumerate(route_trips):
            for scount, stop_seq in enumerate(trips[1:], 1):
                try:
                    to_route_list = routes_by_stop_dict[stop_seq[0]].copy()
                    to_route_list.remove(rr)
                    for r_route in to_route_list:
                        stopindex_by_route = stops_dict[r_route].index(stop_seq[0])
                        for ttcount, tripss in enumerate(stoptimes_dict[r_route]):
                            if tripss[stopindex_by_route][1] >=  change_time + stop_seq[1]:
                                trip_transfer_list.append(
                                    (f"{rr}_{tcount}", scount, f"{r_route}_{ttcount}", stopindex_by_route))
                                break
                except KeyError:
                    pass
                try:
                    for connection in footpath_dict[stop_seq[0]]:
                        to_route_list = routes_by_stop_dict[connection[0]]
                        for r_route in to_route_list:
                            stopindex_by_route = stops_dict[r_route].index(connection[0])
                            for ttcount, tripss in enumerate(stoptimes_dict[r_route]):
                                if tripss[stopindex_by_route][1] >= stop_seq[1] + connection[1]:
                                    trip_transfer_list.append(
                                        (f"{rr}_{tcount}", scount, f"{r_route}_{ttcount}", stopindex_by_route))
                                    break
                except KeyError:
                    pass
        return trip_transfer_list
    
        
        """
