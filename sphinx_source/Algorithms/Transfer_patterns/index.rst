Transfer Patterns
===========================================

The TP algorithm is an efficient transit routing algorithm for solving bicriteria shortest path problems. Consider a journey between two stops a and c described as---board the 0830 bus from a  towards stop b and then board the 0845 bus from b to c. The transfer pattern for this journey can be described as $a-b-c$. Note that none of the in-between stops are mentioned. This kind of representation of journeys not only makes information compact, but also allows for faster lookup. The TP algorithm uses transfer pattern as its fundamental routing unit. The core idea is that the optimal journeys for an OD pair can always be derived from a small fixed subset of transfer patterns. Thus, the routes that do not pass through the transfer patterns can safely be ignored during the query stage. 



.. toctree::
   :maxdepth: 1

   ../../builders/build_transfer_patterns
   transferpattens
   transferpattern_func


Refrences
--------------

For more information refer following:

- Bast, Hannah, et al. "Fast routing in very large public transportation networks using transfer patterns." European symposium on algorithms. Springer, Berlin, Heidelberg, 2010.

- Bast, Hannah, Matthias Hertel, and Sabine Storandt. "Scalable transfer patterns." 2016 Proceedings of the Eighteenth Workshop on Algorithm Engineering and Experiments (ALENEX). Society for Industrial and Applied Mathematics, 2016.
