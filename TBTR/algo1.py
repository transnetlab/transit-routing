""" Build a new transfer set"""
from tqdm import tqdm
import pandas as pd

def build_transfer_set(stoptimes_dict, footpath_dict, routes_by_stop_dict, stops_dict, para, change_time):
    """
    :param stoptimes_dict, footpath_dict, routes_by_stop_dict, stops_dict
    :param para: 1 or 0. If 0, footpaths will not be considered in building trasnsfer set.
    """
    Transfer_set = pd.DataFrame(columns=["from_Trip","from_stop_index","to_trip","to_stop_index"])
    Transfer_set.to_csv(r"./Transfer_set.csv",index=False)
    Transfer_set_list = []
    print("Running Algorithm 1")
    for rr,route_trips in tqdm(stoptimes_dict.items()):
        tcount = -1
        for trips in route_trips:
            tcount = tcount + 1
            scount = -1
            for stop_seq in trips:
                scount = scount + 1
                if scount==0:continue
                try:
                    to_route_list = routes_by_stop_dict[stop_seq[0]]
                    for r_route in to_route_list:
                        if r_route==rr:continue
                        stopindex_by_route = stops_dict[r_route].index(stop_seq[0])
                        ttcount = -1
                        for tripss in stoptimes_dict[r_route]:
                            ttcount = ttcount + 1
                            if tripss[stopindex_by_route][1] - stop_seq[1] > pd.to_timedelta(change_time, unit='seconds'):
                                Transfer_set_list.append((f"{rr}_{tcount}", scount, f"{r_route}_{ttcount}", stopindex_by_route))
                                if len(Transfer_set_list) > 100000:
                                    pd.DataFrame(Transfer_set_list).to_csv(f"./Transfer_set.csv", mode="a", header=False,index=False)
                                    Transfer_set_list = []
                                break
                except KeyError: pass
#                if para==1:
                try:
                    q = footpath_dict[stop_seq[0]]
                    for connection in q:
                        to_route_list = routes_by_stop_dict[connection[0]]
                        for r_route in to_route_list:
                            stopindex_by_route = stops_dict[r_route].index(connection[0])
                            ttcount = -1
                            for tripss in stoptimes_dict[r_route]:
                                ttcount  = ttcount + 1
                                if tripss[stopindex_by_route][1] >= stop_seq[1] + connection[1]:
                                    Transfer_set_list.append((f"{rr}_{tcount}", scount, f"{r_route}_{ttcount}", stopindex_by_route))
                                    if len(Transfer_set_list)>100000:
                                        pd.DataFrame(Transfer_set_list).to_csv(f"./Transfer_set.csv",mode="a", header=False, index=False)
                                        Transfer_set_list = []
                                    break
                except KeyError:pass
    if Transfer_set_list != []:
        pd.DataFrame(Transfer_set_list).to_csv(f"./Transfer_set.csv", mode="a", header=False, index=False)
    pd.read_csv(r"./Transfer_set.csv").to_csv(r"./dict_builder/Transfer_set.csv",index=False)
