"""
Module contains standard Connection Scan Algorithm (CSA) implementation.
"""

from tqdm import tqdm

from CSA.csa_functions import *


def std_csa(SOURCE: int, DESTINATION: int, D_TIME, connections_list: list, WALKING_FROM_SOURCE: int, footpath_dict: dict, PRINT_ITINERARY: int) -> tuple:
    """
    Standard CSA implementation

    Args:
        SOURCE (int): stop id of source stop.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        connections_list:
        WALKING_FROM_SOURCE (int): 1 or 0. 1 indicates walking from SOURCE is allowed.
        footpath_dict (dict): preprocessed dict. Format {from_stop_id: [(to_stop_id, footpath_time)]}.
        PRINT_ITINERARY (int): 1 or 0. 1 means print complete path.

    Returns:
        output (tuple): tuple containing the best arrival time.

    Examples:
        >>> output = std_csa(36, 52, pd.to_datetime('2022-06-30 06:30:00'), connections_list, 1, footpath_dict, 1)
        >>> print(f"Optimal arrival time is: {output}")

    """
    stop_label, trip_set, pi_label, inf_time = initialize_csa(SOURCE, WALKING_FROM_SOURCE, footpath_dict, D_TIME)

    for idx, departure_stop, arrival_stop, departure_time, arrival_time, tid in tqdm(connections_list):
        if departure_time < D_TIME:
            continue
        else:
            if departure_time > stop_label[DESTINATION]:
                if PRINT_ITINERARY == 1:
                    print("Terminated due to time-based target pruning")
                break
            if trip_set[tid] or stop_label[departure_stop] <= departure_time:
                if stop_label[arrival_stop] > arrival_time:
                    stop_label[arrival_stop] = arrival_time
                    pi_label[arrival_stop] = ('connection', idx)
                    trip_set[tid] = True
                    try:
                        for footpath_stop, duration in footpath_dict[arrival_stop]:
                            if stop_label[footpath_stop] > arrival_time + duration:
                                stop_label[footpath_stop] = arrival_time + duration
                                pi_label[footpath_stop] = ("walking", arrival_stop, footpath_stop, duration)
                    except KeyError:
                        pass
    output = post_process_csa(SOURCE, DESTINATION, pi_label, PRINT_ITINERARY, connections_list, stop_label, inf_time)
    return output
