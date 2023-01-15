Trip-based Public Transit Routing
===========================================

TBTR solves the bicriterion (travel time and transfer) optimization problem using trips and trip-transfersas building blocks. TBTR’s search pattern is similarto RAPTOR, but unlike RAPTOR, it does not maintain multi-labels for all stops). TBTR involves a preprocessing and query phase. In its preprocessing  phase, using the GTFS set, we collect all optimal  trip-transfers. The query phase then uses these trip-transfers to answer bicriterion shortest path queries. The codes below only contain the query phase. Currently supported versions are:



.. toctree::
   :maxdepth: 1

   ../../builders/build_TBTR_dict
   tbtr
   rraptor
   one_many_tbtr
   hyptbtr
   TBTR_functions


Refrences
--------------

For more information refer following:

- Agarwal, P., & Rambha, T., 2021. Scalable Algorithms for Bicriterion Trip-Based Transit Routing (Under Review).(https://arxiv.org/abs/2111.06654)

- Witt, S., 2015. Trip-based public transit routing. In Algorithms-ESA 2015 (pp. 1025-1036). Springer, Berlin, Heidelberg.(https://link.springer.com/chapter/10.1007/978-3-662-48350-3_85)