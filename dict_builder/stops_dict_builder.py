"""
Build stop_dict and save it in pickle files in main dir. This is for easy/faster data read in RAPTOR.
syntax = dict[route_id] = [list of stops]
"""
def build_save_stops_dict(stop_times_file,trips_file):
    import pandas as pd
    from tqdm import tqdm
    print("buildig stops dict")

    trips_with_correct_timestamps = []                              #This drops all trips for which timestamps are not sorted
    trips_group = stop_times_file.groupby("trip_id")
    for id, trip in tqdm(trips_group):
        a = pd.Series(list(trip.arrival_time))
        b = pd.Series(list(trip.arrival_time.sort_values().reset_index(drop=True)))
        if all(list(a == b)):
            trips_with_correct_timestamps.append(id)
        else:
            print(f"Incorrecet time sequence in stoptimes builder file {id}")
    stop_times = stop_times_file[stop_times_file["trip_id"].isin(trips_with_correct_timestamps)]

    master_stoptimes = pd.merge(stop_times,trips_file,on=["trip_id"])
    route_groups = master_stoptimes.groupby("route_id")
    stops_dict={}
    for r_id,route_db in route_groups:
        trips_db = route_db.groupby("trip_id")
        for _,trip in trips_db:
            trip = trip.sort_values(by=["stop_sequence"])
            stops_dict.update({r_id: list(trip.stop_id)})
            break

    import pickle
    with open('./dict_builder/stops_dict_pkl.pkl', 'wb') as pickle_file:
        pickle.dump(stops_dict,pickle_file)
    print("stops_dict done")
    return stops_dict
