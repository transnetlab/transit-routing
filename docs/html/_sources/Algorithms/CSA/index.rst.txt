Connection Scan Algorithm
===========================================

CSA is one of the simplest techniques developed for transit routing that does not require a graph. It represents a family of algorithms that uses connections as their fundamental routing unit. Preprocessing and query stages of CSA are described below.

Preprocessing stage: It starts by initializing all the connections in an array, sorted by departure time. Every stop has a label that denotes the earliest arrival time. For a given query, all stop labels except source stop are initialized to infinity.

Query Stage: The basic CSA version (referred to as the Earliest arrival connection scan) scans the connection array from departure time onwards. While scanning a connection, if a stop label is improved, it means a quicker path to the stop has been found. If so, using footpaths we update the labels of neighboring stops. The algorithm stops when optimality is guaranteed.

Currently supported varients of CSA are:


.. toctree::
   :maxdepth: 1

   ../../builders/build_CSA
   std_csa
   csa_functions


Refrences
----------------------------

For more information refer following:

- Dibbelt, Julian, et al. "Connection scan algorithm." Journal of Experimental Algorithmics (JEA) 23 (2018): 1-56.



   
