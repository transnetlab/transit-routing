"""
Build stop_dict and save it in pickle files. This is for easy/faster data read in RAPTOR.
syntax = stoptimes_dict[route ID][trip number][time of stop]
"""

def build_save_stopstimes_dict(stop_times_file,trips_file):
    import pandas as pd
    from tqdm import tqdm
    print("buildig stoptimes dict")

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
    route_group = master_stoptimes.groupby("route_id")
    stoptimes_dict = {}
    for r_id,route in route_group:
        stoptimes_dict[r_id]=[]
        trip_group = route.groupby("trip_id")
        temp = route[route.stop_sequence==0][["trip_id","arrival_time"]]                    #Collect trip start points
        temp.arrival_time = pd.to_datetime(temp.arrival_time)                                  #Sort trips by time
        temp.sort_values(by=["arrival_time"],inplace=True)
        for trip_id in temp["trip_id"]:                                                     #Add them inorder
            trip = trip_group.get_group(trip_id).sort_values(by=["stop_sequence"])
            stoptimes_dict[r_id].append(list(zip(trip.stop_id,pd.to_datetime(trip.arrival_time))))
#            trip.arrival_time = trip.arrival_time.astype(str).apply(lambda x : x[x.find(' ')+1:])
#            stoptimes_dict[r_id].append(list(zip(trip.stop_id,trip.arrival_time.astype(str))))

    import pickle
    with open('./dict_builder/stoptimes_dict_pkl.pkl', 'wb') as pickle_file:
        pickle.dump(stoptimes_dict, pickle_file)
    print("stoptimes_dict_pkl done")
    return stoptimes_dict
