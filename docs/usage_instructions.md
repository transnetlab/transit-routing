****************************************************************************************
*                            TRANSIT ROUTING ALGORITHMS                                *                       
*           Prateek Agarwal                             Tarun Rambha                   *
*        (prateeka@iisc.ac.in)                     (tarunrambha@iisc.ac.in)            *              
****************************************************************************************

## Requirements:
- A 64-bit operating system. Linux, MacOS and Windows are currently supported.
- Python version 3.7 or higher
- Python Modules: tqdm, pandas, numpy, pickle, collections, random, networkx

## Running Test cases:
#### 1. Clone the repository using following command: `git clone link`
#### 2. Run main.py
#### 2. Select following options when prompted:
	algorithm  -> 0 or 1
	variant	   -> 0 or 1 or 2 or 3
	test_case  -> 0
To run algorithms on a different GTFS set, enter the network details in [main.py](main.py). 

## Dataset generation
Due to inconsistencies in the GTFS set available online, a GTFS set cannot be used directly here. 
Moreover, a significant amount of preprocessing (e.g. transitively closed footpaths,
non-overtaking trips etc.) is required. See for details.
The Switzerland test network  is generated in accordance with these.
See [switzerland_wrapper.md](/docs/switzerland_wrapper.py) for documentation on the same. 

## Notes
See [speical_cases.md](/docs/special_cases.py) for details.
