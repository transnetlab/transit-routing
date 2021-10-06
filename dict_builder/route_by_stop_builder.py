"""
Syntax: [stop] = [list of routes]
"""
def build_save_route_by_stop(stop_times_file, folder):
    stops_by_route = stop_times_file.drop_duplicates(subset=['route_id', 'stop_sequence'])[['stop_id', 'route_id']].groupby('stop_id')
    route_by_stop_dict_new = {id:list(routes.route_id) for id, routes in stops_by_route}
    import pickle
    with open(f'./dict_builder/{folder}/routes_by_stop.pkl', 'wb') as pickle_file:
        pickle.dump(route_by_stop_dict_new,pickle_file)
    print("routes_by_stop done")
    return route_by_stop_dict_new


def build_save_route_by_stop_old(stops_dict,stops_file):
    """
    New idea:
        routes_by_stop = defaultdict(lambda: -1)
    stops_group = stoptimes.groupby("stop_id")
    for id, x in stops_group:
        routes_by_stop[id] = tuple(set(x.route))

    """
    from tqdm import  tqdm
    import pandas as pd
    route_by_stop_dict={}
    print("building routes by stop dict..")
    for stop in tqdm(stops_file["stop_id"]):
        routes_serving_p = []
        for route_stop_pair in stops_dict.items():
            if stop in route_stop_pair[1]:
                routes_serving_p.append(route_stop_pair[0])
        if routes_serving_p==[]:
            continue
        route_by_stop_dict.update({stop:routes_serving_p})

    import pickle
    with open('./dict_builder/routes_by_stop.pkl', 'wb') as pickle_file:
        pickle.dump(route_by_stop_dict,pickle_file)
    print("routes_by_stop done")
    return route_by_stop_dict

