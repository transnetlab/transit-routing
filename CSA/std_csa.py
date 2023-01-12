"""
Module contains standard Connection Scan Algorithm (CSA) implementation.
"""

from tqdm import tqdm

from CSA.csa_functions import *


def std_csa(SOURCE: int, DESTINATION: int, D_TIME, connections_list: list, WALKING_FROM_SOURCE: int, footpath_dict: dict, PRINT_ITINERARY: int)->tuple:
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

    """
    stop_label, trip_set, pi_label, inf_time = initialize_csa(SOURCE, WALKING_FROM_SOURCE, footpath_dict, D_TIME)

    for idx, departure_stop, arrival_stop, departure_time, arrival_time, tid in tqdm(connections_list):
        if departure_time < D_TIME:
            continue
        else:
            if stop_label[DESTINATION] <= departure_time:
                if PRINT_ITINERARY == 1:
                    print("Terminated due to time-based target pruning")
                break
            if trip_set[tid] or stop_label[departure_stop] <= departure_time:
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

# FOLDER = './anaheim'
#
# stops_file, trips_file, stop_times_file, transfers_file, stops_dict, stoptimes_dict, footpath_dict, routes_by_stop_dict, idx_by_route_stop_dict, routesindx_by_stop_dict = read_testcase(
#     FOLDER)
#
# SOURCE = 36
# DESTINATION = 68
# DESTINATION_LIST = [53]
# D_TIME = pd.to_datetime('2022-06-30 06:32:17')
# WALKING_FROM_SOURCE = 1
# connections_list = load_connections_dict(FOLDER)
# PRINT_ITINERARY = 1
# breaker = "________________________________________________________________"

#
#
# def csa(SOURCE, DESTINATION, D_TIME, connections_list, WALKING_FROM_SOURCE, footpath_dict, PRINT_ITINERARY):
#     stop_label, trip_set, pi_label = initialize_csa(SOURCE, connections_list, WALKING_FROM_SOURCE, footpath_dict, D_TIME)
#
#     for idx, departure_stop, arrival_stop, departure_time, arrival_time, tid in tqdm(connections_list):
#         if departure_time<D_TIME:continue
#         if stop_label[DESTINATION] <= departure_time:
#             if PRINT_ITINERARY == 1:
#                 print("Terminated due to time-based target pruning")
#             break
#         if trip_set[tid] or stop_label[departure_stop] <= departure_time:
#             stop_label[arrival_stop] = arrival_time
#             pi_label[arrival_stop] = ('connection', idx)
#             trip_set[tid] = True
#             try:
#                 for footpath_stop, duration in footpath_dict[arrival_stop]:
#                     if stop_label[footpath_stop] > arrival_time + duration:
#                         stop_label[footpath_stop] = arrival_time + duration
#                         pi_label[footpath_stop] = ("walking", arrival_stop, footpath_stop, duration)
#             except KeyError:
#                 pass
#     output = post_process_csa(DESTINATION, pi_label, PRINT_ITINERARY, connections_list)
#     return output
#
# def post_process_csa(DESTINATION, pi_label, PRINT_ITINERARY, connections_list):
#     output = None
#     current_stop = DESTINATION
#     if pi_label[current_stop]==-1:
#         if PRINT_ITINERARY == 1:
#             print('DESTINATION cannot be reached')
#     else:
#         journey = []
#         while current_stop != SOURCE:
#             current_label = pi_label[current_stop]
#             print(current_stop)
#             if current_label[0] == 'connection':
#                 connect = connections_list[current_label[1]]
#                 print(connect)
#                 journey.append(connect[1:])
#                 current_stop = connect[1]
#             else:
#                 footpath = current_label[1:]
#                 print(footpath)
#                 journey.append(footpath)
#                 current_stop = current_label[1]
#         connection_journey = list(reversed(journey))
#         if PRINT_ITINERARY == 1:
#             _print_Journey_legs_csv(connection_journey)
#     return output
