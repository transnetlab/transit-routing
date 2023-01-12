"""
Module contains transfer patterns implementation.
"""

from TRANSFER_PATTERNS.transferpattern_func import *


def std_tp(SOURCE: int, DESTINATION: int, D_TIME, footpath_dict: dict, NETWORK_NAME: str, routesindx_by_stop_dict, stoptimes_dict: dict, hub_count: int = 0,
           hubstops: set = set) -> list:
    """
    Standard implementation of trasnfer patterns algorithms. Following functionality is supported regarding hubs:
    1. Build hubs using brute force method. See transferpattern_func

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        NETWORK_NAME (str): GTFS path
        routesindx_by_stop_dict:
        stops_dict (dict): preprocessed dict. Format {route_id: [ids of stops in the route]}.
        hub_count (int):  Number of hub stops
        hubstops (set): set containing id's of stop that are hubs

    Returns:
        pareto optimal journeys

    Examples:
        >>> output = std_tp(36, 52, pd.to_datetime('2022-06-30 05:41:00'), footpath_dict, './anaheim', routesindx_by_stop_dict, stoptimes_dict, 0, set())

    TODO: Add backtracking
    """
    try:
        TP_output = multicriteria_dij(SOURCE, DESTINATION, D_TIME, footpath_dict, NETWORK_NAME, routesindx_by_stop_dict, stoptimes_dict, hub_count, hubstops)
        pareto_journeys = [(item[0], item[1]) for item in TP_output[DESTINATION][2]]
        # print(f"Pareto optimal points: {pareto_journeys}")
        return pareto_journeys
    except FileNotFoundError:
        print("transfer pattern preprocessing incomplete not found")
        return [None]
