"""
Module contains functions to load the GTFS data.
"""
def load_all_dict(FOLDER):
    """
    Args:
        FOLDER (str): Network FOLDER
    Returns:
        stops_dict (dict): Pre-processed dict- format {route_id: [stops]}
        stoptimes_dict (dict): Pre-processed dict- format {route_id: [[trip_1], [trip_2]]}
        footpath_dict (dict): Pre-processed dict- format {from_stop_id: [(to_stop_id, footpath_time)]}
        routes_by_stop_dict (dict): Pre-processed dict- format {stop_id: [routes]}
    """
    import pickle
    with open(f'./dict_builder/{FOLDER}/stops_dict_pkl.pkl','rb') as file:
        stops_dict=pickle.load(file)
    with open(f'./dict_builder/{FOLDER}/stoptimes_dict_pkl.pkl', 'rb') as file:
        stoptimes_dict =pickle.load(file)
    with open(f'./dict_builder/{FOLDER}/transfers_dict_full.pkl', 'rb') as file:
        footpath_dict = pickle.load(file)
    with open(f'./dict_builder/{FOLDER}/routes_by_stop.pkl','rb') as file:
        routes_by_stop=pickle.load(file)
    return (stops_dict, stoptimes_dict, footpath_dict,routes_by_stop)


def load_all_db(FOLDER):
    """
    Args:
        FOLDER (str): Network FOLDER
    Returns:
        stops (pandas.dataframe): dataframe with stop details
        trips (pandas.dataframe): dataframe with trip details
        stop_times (pandas.dataframe): dataframe with stoptimes details
        transfers (pandas.dataframe): dataframe with transfers (footpath) details
    """
    import pandas as pd
    path = f"./GTFS/{FOLDER}"
    stops = pd.read_csv(f'{path}/stops.txt',sep=',').sort_values(by=['stop_id']).reset_index(drop=True)
    trips = pd.read_csv(f'{path}/trips.txt',sep=',')
    stop_times = pd.read_csv(f'{path}/stop_times.csv',sep=',')
    stop_times.arrival_time = pd.to_datetime(stop_times.arrival_time)
#    stop_times_temp = pd.merge(stop_times,trips,on='trip_id')
#    route_groups = stop_times_temp.groupby('route_id')
#    overlapping_trips = []
#    for rid, trip_groups in route_groups:
#        trip_seq = list(trip_groups[trip_groups.stop_sequence==0].sort_values('arrival_time').trip_id)
#        trip_groups = trip_groups.groupby('trip_id')
#        correct_trip = list(trip_groups.get_group(trip_seq[0]).sort_values('arrival_time').arrival_time)
#        for tseq in range(1, len(trip_seq)):
#            check_trip = list(trip_groups.get_group(trip_seq[tseq]).sort_values('stop_sequence')['arrival_time'])
#            if all([check_trip[idx] > correct_stamp for idx,correct_stamp in enumerate(correct_trip)]):
#                correct_trip = check_trip
#            else:
#                overlapping_trips.append(trip_seq[tseq])
#    stop_times = stop_times[~stop_times.trip_id.isin(overlapping_trips)]
    stop_times = pd.merge(stop_times,trips,on='trip_id')
    transfers = pd.read_csv(f'{path}/transfers_full.csv', sep=',')
    return (stops,trips,stop_times,transfers)
