****************************************************************************************
*                            TRANSIT ROUTING ALGORITHMS                                *                       
*           Prateek Agarwal                             Tarun Rambha                   *
*        (prateeka@iisc.ac.in)                     (tarunrambha@iisc.ac.in)            *              
****************************************************************************************

## Switzerland Dataset
- Source - https://transitfeeds.com/ 
- Due to the irregularities in the GTFS set, several preprocessing filters were applied. E.g.
    - Route Ids are integer and start from 1000.
    - Trip Ids string and are of format a_b, where a is route Id and b is the sequence number of the trip when arranged in ascending order (according to departure time from the first stop).
    - Stop Ids are integer and start from 1.
    - Stop sequence in stoptimes.txt file is made continuous.
    - Overlapping trips along a route are removed
    - Disjoint routes (i.e., routes which cannot be reached from any other route in the network) are removed. These generally include waterways, airways.
    - Transfers file in the GTFS set is prepared externally using [OpenStreetMaps](https://www.openstreetmap.org/). Additionally, footpaths are also required to be transitively closed. See References for details.
    - The timetable provided is for a day. All the timestamps are converted into pandas.datetime format.  

- For faster lookup, the GTFS set is post-processed into several dictionaries and provided as pickle files. 
    - stops_dict_pkl: contains stops information.
    - stoptimes_dict_pkl: It provides easy access to the trips along a route.
    - transfers_dict_full: contains footpath details.
    - routes_by_stop: gives access to all the routes ID's passing from a given stop id.
    - idx_by_route_stop: it gives the index of a stop along a route.

  Functions for building these dicts from the GTFS set are present in dict_builder.py. 
- Note: for algorithms working in TBTR environment, an additional TBTR_trip_transfer_dict is defined. For a given trip Id, it stores the list of trip-transfers available from it.
