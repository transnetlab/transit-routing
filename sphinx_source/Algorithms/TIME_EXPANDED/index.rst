Time Expanded Dijkstra
===========================================


In this framework, each event is modeled as a node. An event is defined as a scheduled arrival or departure of a bus/train and each node has a timestamp associated with it. A trip in the TE graph can be defined as a sequence of alternating departure and arrival nodes. Several functions in this module builds on top of NetworkX implementation of Dijkstra's algorithm.

.. toctree::
   :maxdepth: 1

   ../../builders/build_TE
   TE_DIJ
   TE_DIJ_functions


Refrences
----------------------------

For more information refer following:

- Agarwal, P., & Rambha, T., 2021. Scalable Algorithms for Bicriterion Trip-Based Transit Routing (Under Review).(https://arxiv.org/abs/2111.06654)

