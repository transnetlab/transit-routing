"""
This is the Main module.
"""
import pandas as pd

from miscellaneous_func import *

FOLDER = './swiss'

stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict = read_testcase(
    FOLDER)

from tqdm import tqdm
connections_list = []
for route, trip_list in stoptimes_dict.items():
    for tid, trip in enumerate(trip_list):
        connections = list(zip(trip[:-1], trip[1:]))
        connections_list.extend([(from_stop, to_stop, from_time, to_time, f'{route}_{tid}') for ((from_stop, from_time), (to_stop, to_time)) in connections])
connections_db = pd.DataFrame(connections_list, columns=["from_stop", "to_stop","dep_time", "arrival_time", "trip_id"])
ini_len, connections_list = len(connections_db), 0
connections_db = connections_db[(connections_db.from_stop!=connections_db.to_stop) & (connections_db.dep_time!=connections_db.arrival_time) & (connections_db.dep_time<connections_db.arrival_time)]
if len(connections_db)<ini_len:
    print(f"{ini_len - len(connections_db)} connections removed due to inconsistency")
connections_db = connections_db.sort_values(by=["dep_time", 'trip_id']).reset_index(drop=True).reset_index()
connections_db = connections_db.values.tolist()
print(f"{len(connections_db)} connections found")
with open(f'./dict_builder/{FOLDER}/connections_dict_pkl.pkl', 'wb') as pickle_file:
    pickle.dump(connections_db, pickle_file)
print("connections_dict done")

SOURCE = 20775
DESTINATION = 1482
DESTINATION_LIST = [1482]
D_TIME = stop_times_file.arrival_time.sort_values().iloc[0]

def initialize_csa(SOURCE, connections_list, WALKING_FROM_SOURCE):
    from collections import defaultdict
    inf_time = D_TIME.round(freq='H') + pd.to_timedelta("365 day")
    stop_label = defaultdict(lambda : inf_time)
    trip_set = defaultdict(lambda : -1)
    pi_lablel = defaultdict(lambda : -1)
    if WALKING_FROM_SOURCE==1:
        try:
            for to_stop, duration in footpath_dict[SOURCE]:
                stop_label[to_stop] = D_TIME + duration
        except KeyError:pass
    return stop_label, trip_set, pi_lablel

def load_connections_dict(FOLDER):
    import pickle
    with open(f'./dict_builder/{FOLDER}/connections_dict_pkl.pkl', 'rb') as file:
        connections_list = pickle.load(file)
    return connections_list

WALKING_FROM_SOURCE =1
connections_list = load_connections_dict(FOLDER)
stoptimes_dict[9541]
SOURCE = 11713
DESTINATION = 8208
D_TIME = pd.to_datetime('2019-06-10 16:07:50')

stop_label, trip_set, pi_label = initialize_csa(SOURCE, connections_list, WALKING_FROM_SOURCE)
for idx, departure_stop, arrival_stop, departure_time, arrival_time, tid in tqdm(connections_list):
    if stop_label[DESTINATION] <=departure_time:break
    if trip_set[tid] == 0 or stop_label[departure_stop] <= departure_time:
        stop_label[arrival_stop] = arrival_time
        pi_label[arrival_stop] = ('connection', idx)
        trip_set[tid] = 0
        try:
            for footpath_stop, duration in footpath_dict[arrival_stop]:
                if stop_label[footpath_stop]< arrival_time + duration:
                    stop_label[footpath_stop] = arrival_time + duration
                    pi_label[footpath_stop] = ("footpath", arrival_stop, footpath_stop, duration)
        except KeyError:
            pass
current_stop = DESTINATION
label_list = []
11713, 12833, 16405, 8208, 9208, 20767, 22068, 6105, 9543, 19487, 2223
while current_stop!=SOURCE:
    current_label = pi_label[current_stop]
    print(current_stop)
    if current_label[0]=='connection':
        connect = connections_list[current_label[1]]
        print(connect)
        label_list.append(connect[1:])
        current_stop = connect[1]
    else:
        footpath = current_label[1:]
        print(footpath)
        label_list.append(footpath)
        current_stop = current_label[1]

for label in reversed(label_list):
    if len(label)==5:
        print(f"Bus from {label[0]} to {label[1]} along {label[4]}")
    else:
        print(f"Walk from {label[0]} to {label[1]} along {label[2]}")
