Welcome to Transit-routing's documentation!
===========================================

.. image:: _static/logo.png
    :align: center
    :target: https://github.com/transnetlab/transit-routing

Conventional approaches model the transit network as a time-expanded or time-dependent graph and run a variant of the Dijkstra's algorithm. However, this method turns out to be too slow for large networks. Furthermore, while planning a journey using public transit, the number of transfers is equally important besides travel time. Popular techniques developed for PTR in the past decade include---Transfer Patterns algorithm, Connection Scan Algorithm (CSA), Round based Public Transit Routing algorithm (RAPTOR), and Trip-Based public Transit Routing (TBTR) algorithm. This repository provides various efficient algorithms to solve bicriteria shortest path problems in public transit routing. 

We mainly focus on two popular approaches: Round-Based Public Transit Routing (RAPTOR) and Trip-Based public Transit Routing (TBTR) working on arrival time and number of transfers as the two optimization criteria. Apart from the already published HypRAPTOR, we also include our variant of HypTBTR. Furthermore, both HypRAPTOR and HypTBTR have been extended using multilevel partitioning (MhypTBTR and MhypRAPTOR).

Additionally, to make the RAPTOR and TBTR approach more practical, we also include One-To-Many rTBTR and One-To-Many rRAPTOR. These not only reduce the preprocessing times of the partitioning variants but also significantly outperform the existing approach for location-based queries (as a location can have multiple stops near it)

Switzerland's public transit network has been provided as a test case. The figure below shows the transit stop location (left) and 4-way partitioning using KaHyPar (right).

.. image:: _static/location.png
    :align: center


.. list-table:: List of Algorithms
   :widths: 50 50 25 35 15 
   :header-rows: 1

   * - Algorithms
     - Varient
     - Source
     - Status
     - Comments
   * - Time-Expanded Graph
     - Dijkstra Algorithm
     -   `link <https://arxiv.org/abs/2111.06654>`_
     - Complete
     - 
   * - RAPTOR
     - Standard RAPTOR
     -   `link <https://pubsonline.informs.org/doi/abs/10.1287/trsc.2014.0534/>`_
     - Complete
     - 
   * - RAPTOR
     - rRAPTOR
     -   `link <https://pubsonline.informs.org/doi/abs/10.1287/trsc.2014.0534/>`_
     - Complete
     - 
   * - RAPTOR
     - HypRAPTOR
     -   `link <https://drops.dagstuhl.de/opus/volltexte/2017/7896/>`_
     - Complete
     - 
   * - RAPTOR
     - One-To-Many rRAPTOR
     -   `link <https://arxiv.org/abs/2111.06654>`_
     - To be added soon
     - 
   * - TBTR
     - Standard TBTR
     -   `link <https://link.springer.com/chapter/10.1007/978-3-662-48350-3_85>`_
     - Complete
     - 
   * - TBTR
     - rTBTR
     -   `link <https://link.springer.com/chapter/10.1007/978-3-662-48350-3_85>`_
     - Complete
     - 
   * - TBTR
     - One-To-Many rTBTR
     -   `link <https://arxiv.org/abs/2111.06654>`_
     - Complete
     - 
   * - TBTR
     - HypTBTR
     -   `link <https://arxiv.org/abs/2111.06654>`_
     - Complete
     - 
   * - TBTR
     - MHypTBTR
     -   `link <https://arxiv.org/abs/2111.06654>`_
     - Complete
     - 
   * - TBTR
     - MHypTBTR
     -   `link <https://arxiv.org/abs/2111.06654>`_
     - Complete
     - 
   * - Transfer Patterns 
     - Standard TP 
     -   `link <https://link.springer.com/chapter/10.1007/978-3-642-15775-2_25>`_
     - Complete
     - 
   * - Transfer Patterns 
     - Scalable TP
     -   `link <https://epubs.siam.org/doi/abs/10.1137/1.9781611974317.2>`_
     - To be addeed soon
     - 
   * - Connection Scan Algorithm
     - Standard CSA
     -   `link <https://epubs.siam.org/doi/abs/10.1137/1.9781611974317.2>`_
     - Complete
     - 

Navigation
------------

.. toctree::
   :maxdepth: 1

   quickstart
   GTFS_preprocessing
   Algorithms
   miscellaneous

Contributing
------------
We welcome all suggestions from the community. If you wish to contribute or report any bug please contact the creaters or create an issue on 
`issue tracking system <https://github.com/transnetlab/transit-routing/issues>`_.



Creators
------------


1. **Prateek Agarwal**
    - Ph.D. at `Indian Institute of Science Bengaluru India <https://iisc.ac.in/>`_
    - Website: `<https://sites.google.com/view/prateek-agarwal/>`_
    - Mail Id: prateeka@iisc.ac.in
    

2. **Tarun Rambha**
    - Assistant Professor in the Civil Engineering and the Center for Infrastructure, Sustainable Transportation and Urban Planning (CiSTUP) at `Indian Institute of Science Bengaluru India <https://iisc.ac.in/>`_.
    - Website: `http://civil.iisc.ernet.in/~tarunr/ <http://civil.iisc.ernet.in/~tarunr/>`_
    - Mail Id: tarunrambha@iisc.ac.in


Copyright and license
------------------------
The content of this repository is bounded by MIT License. For more information see `COPYING file <https://github.com/transnetlab/transit-routing/blob/main/LICENSE>`_ 
