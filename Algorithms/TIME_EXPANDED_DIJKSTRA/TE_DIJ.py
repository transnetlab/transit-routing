"""
Implementation of Dijkstra's algorithm on a Time expanded Graph.
"""

from Algorithms.TIME_EXPANDED_DIJKSTRA.TE_DIJ_functions import *


def custom_dij(SOURCE: int, DESTINATION: int, D_TIME, G, stops_group, stopevent_mapping: dict, stop_times_file) -> tuple:
    """
    Custom dijkstra's algorithm. This functions builds on top of networkx implementation of Dijkstra's algorithm.

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        G: Time expanded graph. Foramt: Networkx Digraph.
        stops_group: stoptimes file group by stopid
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        stopevent_mapping (dict): Format: {sequence_no: (stop_id, stop event)}

    Returns:
        tuple

    Examples:
        >>> output = custom_dij(36, 52, pd.to_datetime('2022-06-30 05:41:00'), G, stops_group, stopevent_mapping, stop_times_file)

    """
    source_node = get_sourcenode(stops_group, SOURCE, D_TIME, stopevent_mapping)
    idx, target_list = get_possible_targets(stops_group, DESTINATION, D_TIME, stopevent_mapping)

    weight = weight_function(G, 'weight')
    out_dist = edited_dijkstra_multitarget(G, source_node, target_list, weight)

    stop_reached, time_reached = post_process_TE_DIJ(out_dist, target_list, stop_times_file, D_TIME, idx)
    return stop_reached, time_reached
