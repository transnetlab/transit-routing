
def optiaml_trans(stoptimes_dict,footpath_dict):
    print("Running Algorithm 3")
    import pandas as pd
    from collections import defaultdict
    from tqdm import tqdm
    import pickle

    with open('./dict_builder/trip_transfer_dict_partial.pkl', 'rb') as file:
        trip_transfer_dict = pickle.load(file)

    init_tans = 0
    for x in trip_transfer_dict.values():
        init_tans = init_tans + len(x)

    inf_time = pd.Timestamp(year=2022, month=1, day=1, hour=1, second=1)
    for r_id,route_trips in tqdm(stoptimes_dict.items()):
        for t_id, trip in enumerate(route_trips):
            stop_labels = defaultdict(lambda :inf_time)
            trip_rev = list(reversed(list(enumerate(trip))))
            for s_idx, stop_seq in trip_rev:
                stop_labels[stop_seq[0]] = min(stop_labels[stop_seq[0]], stop_seq[1])
                try:
                    for q in footpath_dict[stop_seq[0]]:
                        stop_labels[q[0]] = min(stop_labels[q[0]], stop_seq[1]+q[1])
                except KeyError:pass
                try:
                    for trans in trip_transfer_dict[f"{r_id}_{t_id}"]:
                        if trans[0]!=s_idx:continue
                        breakdown = [int(x) for x in trans[1].split("_")]
                        keep = False
                        for stop_connect in stoptimes_dict[breakdown[0]][breakdown[1]][trans[2]+1:]:
                            keep = keep or (stop_connect[1]<stop_labels[stop_connect[0]])
                            stop_labels[stop_connect[0]] = min(stop_labels[stop_connect[0]], stop_connect[1])
                            try:
                                for footpath_connect in footpath_dict[stop_connect[0]]:
                                    eta = stop_connect[1] + footpath_connect[1]
                                    keep = keep or (eta<stop_labels[footpath_connect[0]])
                                    stop_labels[footpath_connect[0]] = min(stop_labels[footpath_connect[0]],eta)
                            except KeyError:pass
                        if not keep:
                            a = [*trans]
                            a.insert(0, f"{r_id}_{t_id}")
#                            print(a)
                            trip_transfer_dict[f"{r_id}_{t_id}"].remove(trans)
                except KeyError:pass

    final_trans = 0
    for x in trip_transfer_dict.values():
        final_trans = final_trans + len(x)
    print(f"2nd step reduced {int(((init_tans-final_trans)/init_tans)*100)}% transfers")

    trip_transfer_dict_new = {}
    for tid, connections in tqdm(trip_transfer_dict.items()):
        trip_transfer_dict_new[tid] = {}
        for x in connections:
            if x[0] not in trip_transfer_dict_new[tid].keys():
                trip_transfer_dict_new[tid][x[0]] = []
            trip_transfer_dict_new[tid][x[0]].append((x[1], x[2]))
    with open('trip_transfer_dict.pkl', 'wb') as pickle_file:
        pickle.dump(trip_transfer_dict_new, pickle_file)
    with open('./dict_builder/trip_transfer_dict.pkl', 'wb') as pickle_file:
        pickle.dump(trip_transfer_dict_new, pickle_file)
    print("trip_Transfer_dict done final")
