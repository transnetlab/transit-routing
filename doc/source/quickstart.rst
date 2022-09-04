Quickstart
==========

Requirements
------------
- A 64-bit operating system. Linux, MacOS and Windows are currently supported.
- Python version 3.7 or higher
- Python Modules: tqdm, pandas, numpy, pickle, collections, random, networkx


Running Test cases
-------------------
 1. Clone the repository using following command: `gh repo clone transnetlab/transit-routing`
 2. Run main.py
 2. Select following options when prompted:
   ``algorithm  -> 0 or 1``

   ``variant     -> 0 or 1 or 2 or 3``

   ``test_case  -> 0``

To run algorithms on a different GTFS set, enter the network details in [main.py](https://github.com/transnetlab/transit-routing/blob/main/main.py). 

Dataset generation
------------------
Due to inconsistencies in the GTFS sets available online, they cannot be used directly. 
Moreover, a significant amount of preprocessing (e.g., transitively closed footpaths,
non-overtaking trips, continuous stop sequence) is required. The Switzerland test network
is generated in accordance with these.  See [switzerland_wrapper.md](./switzerland_wrapper.md) 
for documentation on the same. 

Additional notes
------------------
- To print complete itinerary, set PRINT_ITINERARY = 1 and OPTIMIZED = 0.
- Additional target pruning is applied in the footpath phase of all RAPTOR related algorithms.
- To compare the output of RAPTOR and TBTR, WALKING_FROM_SOURCE must be set to 1.
- Post processing in rRAPTOR and rTBTR gives the set of optimal trips (or routes id OPTIMIZED=0) required to cover all optimal journeys. However, the output set by rRAPTOR and rTBTR might not match. To understand this, imagine two different journeys with the same arrival times and number of transfers. Since, all algorithms are coded using strict dominance, only one of the two will be detected. While the rRAPTOR might include the first journey, rTBTR can include second. In such cases, algorithm's correctness can be checked by comparing the optimal arrival times (which should be same).

