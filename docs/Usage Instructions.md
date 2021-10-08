****************************************************************************************
*                            TRANSIT ROUTING ALGORITHMS                                *                       
*           Prateek Agarwal                             Tarun Rambha                   *
*        (prateeka@iisc.ac.in)                     (tarunrambha@iisc.ac.in)            *              
****************************************************************************************

## Requirements:
- A 64-bit operating system. Linux, Mac OS X and Windows are currently supported.
- Python version 3.7 or higher
- Python Modules: tqdm, pandas, numpy, pickle, collections, random, networkx

## Running Test cases:
#### 1. Clone the repository using following command: `git clone link`
#### 2. Run main.py
#### 2. Select following options when prompted:
	algorithm  -> 0 or 1
	varient	   -> 0 or 1 or 2 or 3
	test_case  -> 0

To run algorithms on a different GTFS set, enter the network details in [main.py](main.py). Note that due to inconsistencies in the 
GTFS set avaliable online, not every transit network can be directly used. Moreover, a significant amount of preprocessing (e.g. transiteively closed footpaths, 
non-overtaking trips etc.) is required. See for details. 
The Switzerland test network  is generated in accordance with these. [Switzerland_wrapper.py](Switzerland_wrapper.py) contains the code for the same.
See [Switzerland_wrapper.md](/docs/\Switzerland_wrapper.py) for documentation on the same. 

