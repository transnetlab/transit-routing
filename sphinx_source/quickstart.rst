Quickstart
==========

Requirements
----------------
- A 64-bit operating system. Linux, MacOS and Windows are currently supported.
- Python version 3.7 or higher
- Python Modules: tqdm, pandas, numpy, pickle, networkx


Running Test cases
-------------------
 #. Clone the repository using following command:

    .. code-block:: bash

       git clone https://github.com/transnetlab/transit-routing.git

 #. Enter following commands. In case of error, edit `main.py <https://github.com/transnetlab/transit-routing/blob/main/main.py>`_

    .. code-block:: bash

         cd transit-routing
         pip install -r requirements.txt
         python main.py

 #. Enter following parameters when prompted:

    .. code-block:: python

        Network name: anaheim
        Date: 20220630
        Bus routes: 3, -1
        build transfers file: 0
        build TBTR files: 0
        build CSA files: 0
        build Transfer Pattern files: 0
        build Time Expanded files: 0
        use test case: 1
        RAPTOR environment: 0
        Standard RAPTOR: 0

 #. Following output should be displayed:

    .. code-block:: python

         ___________________Query Parameters__________________
         Network: ./anaheim
         SOURCE stop id: 36
         DESTINATION stop id: 52
         Maximum Transfer allowed: 4
         Is walking from SOURCE allowed ?: 1
         Earliest departure time: 2022-06-30 05:41:00
         _____________________________________________________
         from 36 walk till  38.0 for 337.2 seconds
         from 38 board at 06:38:18 and get down on 1 at 06:41:53 along 1020_0
         from 1 walk till  17.0 for 171.7 seconds
         from 17 board at 06:53:44 and get down on 30 at 06:55:53 along 1025_1
         from 30 walk till  53.0 for 124.7 seconds
         from 53 board at 07:14:00 and get down on 68 at 07:20:00 along 1018_2
         from 68 board at 15:00:00 and get down on 52 at 15:12:00 along 1030_0
         ####################################
         from 36 walk till  38.0 for 337.2 seconds
         from 38 board at 06:38:18 and get down on 1 at 06:41:53 along 1020_0
         from 1 board at 18:30:00 and get down on 35 at 18:31:50 along 1014_0
         from 35 walk till  51.0 for 85.2 seconds
         from 51 board at 18:37:00 and get down on 52 at 18:42:00 along 1012_0
         ####################################
         Optimal arrival time are: [[Timestamp('2022-06-30 15:12:00'), Timestamp('2022-06-30 18:42:00')]]


Running your instance
-------------------------
Due to inconsistencies in the GTFS sets available online, they cannot be used directly.
A significant amount of preprocessing (e.g., transitively closed footpaths,
non-overtaking trips, continuous stop sequence) is required. `GTFS_wrapper.py <https://github.com/transnetlab/transit-routing/blob/main/GTFS_wrapper.py>`_ provides the functions to convert GTFS set into required format. See GTFS preprocessing for further details.


Rename your GTFS.zip to network_GTFS.zip (e.g., anaheim_GTFS.zip) and place it in main directory. Run `main.py <https://github.com/transnetlab/transit-routing/blob/main/main.py>`_ and
enter the variables accordingly.

Once the GTFS set is processed successfully, directly run `query_file.py <https://github.com/transnetlab/transit-routing/blob/main/query_file.py>`_ to find optiaml journeys.

Additional notes
------------------
- To print complete itinerary, set **PRINT_ITINERARY** = 1 and **OPTIMIZED** = 0.
- Additional target pruning is applied in the footpath phase of all RAPTOR related algorithms.
- To compare the output of RAPTOR and TBTR, **WALKING_FROM_SOURCE** must be set to 1.
- Post processing in rRAPTOR and rTBTR gives the set of optimal trips (or routes id **OPTIMIZED**=0) required to cover all optimal journeys. However, the output set by rRAPTOR and rTBTR might not match. To understand this, imagine two different journeys with the same arrival times and number of transfers. Since, all algorithms are coded using strict dominance, only one of the two will be detected. While the rRAPTOR might include the first journey, rTBTR can include second. In such cases, algorithm's correctness can be checked by comparing the optimal arrival times (which should be same).

