"""
Load GTFS. Functions for both dict and files are present.
"""

def load_all_dict(full_trans):
    import pickle
    with open('./dict_builder/stops_dict_pkl.pkl','rb') as file:
        stops_dict=pickle.load(file)
    with open('./dict_builder/stoptimes_dict_pkl.pkl', 'rb') as file:
        stoptimes_dict =pickle.load(file)
    if full_trans==1:
        with open('./dict_builder/transfers_dict_full.pkl', 'rb') as file:
            transfers_dict = pickle.load(file)
    else:
        with open('./dict_builder/transfers_dict.pkl', 'rb') as file:
            transfers_dict = pickle.load(file)
    with open('./dict_builder/routes_by_stop.pkl','rb') as file:
        routes_by_stop=pickle.load(file)
    return (stops_dict,stoptimes_dict,transfers_dict,routes_by_stop)

def load_all_db(full_trans):
    import pandas as pd
    path="./GTFS"
    stops=pd.read_csv(f'{path}/stops.txt',sep=',')
    routes=pd.read_csv(f'{path}/routes.txt',sep=',')
    trips=pd.read_csv(f'{path}/trips.txt',sep=',')
    stop_times=pd.read_csv(f'{path}/stoptimes.csv',sep=',')
    if full_trans==1:
        transfers = pd.read_csv(f'{path}/transfers_full.csv', sep=',')
    else:
        transfers = pd.read_csv(f'{path}/transfers.txt', sep=',')
    return (stops,routes,trips,stop_times,transfers)
