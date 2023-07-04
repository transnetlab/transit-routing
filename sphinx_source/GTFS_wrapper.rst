Functions realted to GTFS Wrapper
========================================

- Due to the irregularities in the GTFS set, several preprocessing filters were applied. E.g.
    - Route Ids are integer and start from 1000.
    - Trip Ids string of format a_b, where a is route Id and b is the sequence number of the trip when arranged in ascending order (according to departure time from the first stop).
    - Stop Ids are integer and start from 1.
    - Stop sequence in stoptimes.txt file is made continuous.
    - Overlapping trips along a route are removed
    - Disjoint routes (i.e., routes which cannot be reached from any other route in the network) are removed. These generally include waterways, airways.
    - The timetable provided is for a day. All the timestamps are converted into pandas.datetime format.
    - calendar_dates can be used in two sense. In the first case, it acts as a supplement to calendar.txt by defining listing the service id removed or added on a particular day (recommended usage).In the second case, it acts independently by listing all the service active on the particular day. See  GTFS reference for more details. Currently only first type of functionality is supported. 

For implementation details, see `GTFS_wrapper.py <https://github.com/transnetlab/transit-routing/blob/main/GTFS_wrapper.py>`_.

Description
-----------------------------

.. automodule:: GTFS_wrapper
   :members:

