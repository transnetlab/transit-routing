"""
THis is the main module.
"""

import os

os.system('python GTFS_wrapper.py')
os.system('python build_transfer_file.py')
os.system('python TBTR_dict_builder.py')
os.system('python query_file.py')