"""
This module contains functions related to Time-expanded Dijkstra's algorithm
"""
from itertools import count

import pandas as pd


def get_sourcenode(stops_group, SOURCE: int, D_TIME, stopevent_mapping: dict) -> int:
    """
    Using the earliest arrival event from the source node (after D_TIME), find the ID of the node in TE graph.
    This serves as source stop for Dijkstra's algorithm.

    Args:
        stops_group: pandas group object on stoptimes file using stop id column.
        SOURCE (int): stop id of source stop.
        D_TIME (pandas.datetime): departure time.
        stopevent_mapping (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Returns:
        source_node (int): Source node Id corresponding to TE graph

    Examples:
        >>> source_node = get_sourcenode(stops_group, 36, pd.to_datetime('2019-06-10 00:00:00'), stopevent_mapping)

    """
    source_node_db = stops_group.get_group(SOURCE).sort_values(by='arrival_time')
    source_node = tuple(source_node_db[source_node_db.arrival_time > D_TIME][['stop_id', 'arrival_time']].iloc[0])
    source_node = stopevent_mapping[source_node]
    return source_node


def get_possible_targets(stops_group, DESTINATION: int, D_TIME, stopevent_mapping: dict) -> tuple:
    """
    Get the list of events from DESTINATION stop Id after D_TIME. These serve as possible target nodes for Dijkstra's algorithm

    Args:
        stops_group: pandas group object on stoptimes file using stop id column.
        DESTINATION (int): stop id of destination stop.
        D_TIME (pandas.datetime): departure time.
        stopevent_mapping (dict): mapping dictionary. Format: {(stop id, arrival time): new node id}

    Returns:
        idx (tuple): tuple containing Indexes of the reachable event of target node in stoptimes file
        target_list (tuple): tuple containing node Id corresponding reachable target nodes of to TE graph

    Examples:
        >>> idx, target_list = get_possible_targets(stops_group, 52, pd.to_datetime('2019-06-10 00:00:00'), stopevent_mapping)

    """
    desti_nodes = stops_group.get_group(DESTINATION).sort_values(by='arrival_time')
    desti_nodes1 = desti_nodes[desti_nodes.arrival_time > D_TIME][['stop_id', 'arrival_time']].drop_duplicates()
    idx, target_list = zip(*[(idx, stopevent_mapping[tuple(x)]) for idx, x in desti_nodes1.iterrows()])
    return idx, target_list


def _siftdown(heap, startpos, pos):
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    while pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        if newitem < parent:
            heap[pos] = parent
            pos = parentpos
            continue
        break
    heap[pos] = newitem


def _siftup(heap, pos):
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the smaller child until hitting a leaf.
    childpos = 2 * pos + 1  # leftmost child position
    while childpos < endpos:
        # Set childpos to index of smaller child.
        rightpos = childpos + 1
        if rightpos < endpos and not heap[childpos] < heap[rightpos]:
            childpos = rightpos
        # Move the smaller child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2 * pos + 1
    # The leaf at pos is empty now.  Put newitem there, and bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown(heap, startpos, pos)


def heappush(heap, item):
    """Push item onto heap, maintaining the heap invariant."""
    heap.append(item)
    _siftdown(heap, 0, len(heap) - 1)


def heappop(heap):
    """Pop the smallest item off the heap, maintaining the heap invariant."""
    lastelt = heap.pop()  # raises appropriate IndexError if heap is empty
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup(heap, 0)
        return returnitem
    return lastelt


def edited_dijkstra_multitarget(G, SOURCE: int, target_list: tuple, weight) -> dict:
    """
    Uses Dijkstra's algorithm to find shortest weighted paths. This functions builds on top of networkx implementation of Dijkstra's algorithm

    Args:
        G: NetworkX graph
        SOURCE : non-empty iterable of nodes
            Starting nodes for paths. If this is just an iterable containing
            a single node, then all paths computed by this function will
            start from that node. If there are two or more nodes in this
            iterable, the computed paths may begin from any one of the start
            nodes.
        target_list : node label, optional
            Ending node for path. Search is halted when target is found.
        weight: function
            Function with (u, v, data) input that returns that edges weight

    Returns:
        distance : dictionary
            A mapping from node to shortest distance to that node from one
            of the SOURCE nodes.

    Examples:
        >>> dist = edited_dijkstra_multitarget(G, SOURCE, target_list, weight)

    """
    G_succ = G._succ if G.is_directed() else G._adj

    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {}
    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()
    fringe = []
    seen[SOURCE] = 0
    push(fringe, (0, next(c), SOURCE))
    while fringe:
        (d, _, v) = pop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        if v in target_list:
            break
        for u, e in G_succ[v].items():
            cost = weight(v, u, e)
            if cost is None:
                continue
            vu_dist = dist[v] + cost
            if u in dist:
                u_dist = dist[u]
                if vu_dist < u_dist:
                    raise ValueError("Contradictory paths found:", "negative weights?")
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, next(c), u))
    return dist


def weight_function(G, weight):
    """
    (Borrowed from NetworkX)
    Returns a function that returns the weight of an edge.

    The returned function is specifically suitable for input to
    functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

    Parameters
    ----------
    G : NetworkX graph.

    weight : string or function
        If it is callable, `weight` itself is returned. If it is a string,
        it is assumed to be the name of the edge attribute that represents
        the weight of an edge. In that case, a function is returned that
        gets the edge weight according to the specified edge attribute.

    Returns
    -------
    function
        This function returns a callable that accepts exactly three inputs:
        a node, an node adjacent to the first one, and the edge attribute
        dictionary for the eedge joining those nodes. That function returns
        a number representing the weight of an edge.

    If `G` is a multigraph, and `weight` is not callable, the
    minimum edge weight over all parallel edges is returned. If any edge
    does not have an attribute with key `weight`, it is assumed to
    have weight one.

    """
    if callable(weight):
        return weight
    # If the weight keyword argument is not callable, we assume it is a
    # string representing the edge attribute containing the weight of
    # the edge.
    if G.is_multigraph():
        return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
    return lambda u, v, data: data.get(weight, 1)


def post_process_TE_DIJ(out_dist: dict, target_list: tuple, stop_times_file, D_TIME, idx: tuple) -> tuple:
    """
    Post processing for TE_DIJ

    Args:

        out_dist (dict): Distance dictionary of format {node id : arrival time}
        target_list (tuple): tuple containing node Id corresponding reachable target nodes of to TE graph
        stop_times_file (pandas.dataframe): stop_times.txt file in GTFS.
        D_TIME (pandas.datetime): departure time.
        idx (tuple): tuple containing Indexes of the reachable event of target node in stoptimes file

    Returns:
        stop_reached (tuple): Stop event that is reached
        time_reached (pandas.timestamp): arrival time at the stop event

    Examples:
        >>> stop_reached, time_reached = post_process_TE_DIJ(out_dist, target_list, stop_times_file, pd.to_datetime('2019-06-10 00:00:00'), idx)

    """
    out_dist1 = [(node, out_dist[node]) for node in target_list if node in out_dist.keys()]
    if len(out_dist1) == 0:
        print("No path exists")
        return None, None
    elif len(out_dist1) == 1:
        final_result = out_dist1[0]
        stop_reached = tuple(stop_times_file.iloc[idx[target_list.index(final_result[0])]][['stop_id', 'arrival_time']])
        #    [x[0] for x in nodes_dict.items() if x[1]==final_result[0]]
        time_reached = D_TIME + pd.to_timedelta(final_result[1], unit='seconds')
        print(f"Stop Event {stop_reached} was reached at {time_reached} ")
        return stop_reached, time_reached
    else:
        out_dist1.sort(key=lambda x: x[1])
        final_result = out_dist1[0]
        print("Warning: Error in TE_DIJ. Check why is output length >1")
        return None, None
