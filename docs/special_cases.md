****************************************************************************************
*                            TRANSIT ROUTING ALGORITHMS                                *                       
*           Prateek Agarwal                             Tarun Rambha                   *
*        (prateeka@iisc.ac.in)                     (tarunrambha@iisc.ac.in)            *              
**************************************************************************************** 
## Notes:

- Additional target pruning is applied in the footpath phase of all RAPTOR related algorithms.
- While comparing the output of RAPTOR and TBTR, varaible WALKING_FROM_SOURCE must be set to 1.  
- Post processing in rRAPTOR and rTBTR gives the set of optimal trips (or routes id OPTIMIZED=0) required to cover all optimal journeys. However, the output set by rRAPTOR and rTBTR might not match. To understand this, imagine two different journeys with the same arrival times and number of transfers. Since, all algorithms are coded using strict dominance, only one of the two will be detected. While the rRAPTOR might include the first journey, rTBTR can include second. In such cases, algorithm's correctness can be checked by comparing the optimal arrival times (which should be same).
