import pickle
import pandas as pd
import networkx as nx

def check(stops_dict,stoptimes_dict,stop_times_file):
    """
    Do not check route stops wrt route point file as somestops have been deleted while building these dict
    """
    if not stops_dict.keys()==stoptimes_dict.keys():
        print(f"route are different in stopsdict and stoptimes dict")
    for stopdict_r_id,stopdict_r_stops in stops_dict.items():
        trips = stoptimes_dict[stopdict_r_id]
        for temp_index in range(len(trips)):
            stoptime_stops, stoptime_times = list(zip(*trips[temp_index]))
            if not list(stoptime_stops)==stopdict_r_stops:
                print(f"stops seq differ in stoptimes and stop dict for id {stopdict_r_id}")
            for stamps in range(len(stoptime_times)-1):
                if not stoptime_times[stamps+1]>= stoptime_times[stamps]:
                    print(f"timestamps seq error in stoptimes {stopdict_r_id} for tripid {temp_index}")
#    print(f"stop_dict and stoptimes_dict check complete")


def check_nonoverlap(stoptimes_dict):
    """Trips in a network should not be overlapping"""
    overlap = set()
    for r_idx, route_trips in stoptimes_dict.items():
        trip_len = len(route_trips[0])
        for x in range(len(route_trips)-1):
            first_trip = route_trips[x]
            second_trip = route_trips[x+1]
            for idx in range(trip_len):
                if second_trip[idx][1] < first_trip[idx][1]:
                    overlap = overlap.union({r_idx})
    return overlap


def reduce_net(stoptimes_dict):
    route_list = [5695, 7362, 7364, 9375, 12027,  12035, 13342, 18562, 19344, 19396,  20573, 20574, 20790, 20854, 22389, 22511, 23021, 23478, 24028,  29536, 29537, 29742, 29928, 30485, 31649, 33447, 33961, 33962, 34531,  35174, 39118, 39268, 39269, 41266,41267]

    for x in stoptimes_dict.keys():
        if x not in route_list:
            stoptimes_dict[x] = []
    return stoptimes_dict

def get_full_trans(time_limit):
    print('editing transfers')
    transfers_file = pd.read_csv(f'./GTFS/transfers.txt', sep=',')
    transfers_file = transfers_file[transfers_file.min_transfer_time < time_limit].reset_index(drop=True)
    G = nx.Graph()
    # G.add_weighted_edges_from([(1, 2, 3), (2, 3, 3), (3, 4, 3) ,(1, 4, 3), (1, 5, 3), (5, 6, 3), (5, 7, 3)])
    edges = list(zip(transfers_file.from_stop_id, transfers_file.to_stop_id, transfers_file.min_transfer_time))
    G.add_weighted_edges_from(edges)
#    len(G.edges), len(edges)
    connected = [c for c in nx.connected_components(G)]
    # nx.draw(G, with_labels = True)
    for tree in connected:
        for source in tree:
            for desti in tree:
                if source != desti and (source, desti) not in G.edges():
                    G.add_edge(source, desti, weight=nx.dijkstra_path_length(G, source, desti))
    footpath = list(G.edges(data=True))
    for x in G.edges(data=True):
        footpath.append((x[1], x[0], x[-1]))
    footpath_db = pd.DataFrame(footpath)
    footpath_db[2] = footpath_db[2].apply(lambda x: list(x.values())[0])
    footpath_db.rename(columns={0: "from_stop_id", 1: "to_stop_id", 2: "min_transfer_time"}, inplace=True)
    footpath_db.to_csv(f'./GTFS/transfers_full.csv',index=False)

    transfers_dict={}
    g=footpath_db.groupby("from_stop_id")
    for from_stop,details in g:
        transfers_dict[from_stop]=[]
        for _,row in details.iterrows():
            transfers_dict[from_stop].append((row.to_stop_id,pd.to_timedelta(float(row.min_transfer_time),unit='seconds')))
    with open('./dict_builder/transfers_dict_full.pkl', 'wb') as pickle_file:
        pickle.dump(transfers_dict,pickle_file)


def check_footpath(footpath_dict):
    edges = []
    for from_s,to_s in footpath_dict.items():
        to_s, _ = zip(*to_s)
        edges.extend([(from_s,x) for x in to_s])
    G = nx.Graph()
    G.add_edges_from(edges)

    connected = [c for c in nx.connected_components(G)]
    for connected_comp in connected:
        for source in connected_comp:
            for desti in connected_comp:
                if source == desti: continue
                if (source, desti) not in G.edges():
                    print('error in footpath dict')
                    print(source, desti)
    return 0

