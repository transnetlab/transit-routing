****************************************************************************************
*                            TRANSIT ROUTING ALGORITHMS                                *                       
*           Prateek Agarwal                             Tarun Rambha                   *
*        (prateeka@iisc.ac.in)                     (tarunrambha@iisc.ac.in)            *              
****************************************************************************************

## Switzerland Dataset
- Source - https://transitfeeds.com/ (pre-Covid data)
- Due to the irregularities in the GTFS set, several preprocessing filters were applied. E.g.
    - Route Ids start from 1000.
    - Trip Ids are of format a_b, where a is route Id and b is the sequence number of the trip when arranged in ascending order (according to departure time from the first stop).
    - Stop Ids start from 1.
    - Overlapping trips along a route are removed
    - Disjoint routes (i.e., routes which cannot be reached from any other route in the network) are removed. These generally include waterways, airways.
    - Transfers file in the GTFS set is prepared externally using [OpenStreetMaps](https://www.openstreetmap.org/). Additionally, Footpaths are also required to be transitively closed. See References for details.
    - The timetable provided is a day. All the timestamps are converted into pandas.datetime format.  

  After applying the above filters, stop_times.txt is saved as stop_times.csv
- For faster lookup, the GTFS set is post-processed into several dictionaries and saved as pickle files. 
    - stops_dict_pkl: contains stops information.
    - stoptimes_dict_pkl: It provides easy access to the trips along a route.
    - transfers_dict_full: contains footpath details.
    - routes_by_stop: gives access to the routes passing from a given stop id.
    - idx_by_route_stop: it gives the index of a stop along a route.

  Functions for building these dicts from the GTFS set are present in dict_builder.py. Note: for algorithm's working in TBTR environment, an additional TBTR_trip_transfer_dict is defined. For a given trip Id, it stores the list of trip-transfers available from it.
