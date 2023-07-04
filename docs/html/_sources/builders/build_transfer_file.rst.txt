Functions realted to building transfers file.
==============================================

- `build_transfer_file.py <https://github.com/transnetlab/transit-routing/blob/main/build_transfer_file.py>`_. has been provided to transfers_file.txt. This module requires OSMNX package. Following inputs are required:
    - The graph (if not found on disk) is extracted using `OpenStreetMaps <https://www.openstreetmap.org/#map=4/21.84/82.79>`_    
    - For every stop, shortest path comutation is performaed within a radius maximum walking limit.
    - Ensures the transitive closure of footpaths. 
  Following additional inputs are required. 
    - WALKING_LIMIT (int)- Maximum allowed walking time. Note that the final transfers file can have longer transfers due to transitive closure. 
    - CORES (int): Number of codes to be used. Shortest path computation can be done in parallel. 

Description
--------------

.. automodule:: builders.build_transfer_file
   :members:

