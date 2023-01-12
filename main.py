"""
This is the main module.
"""

import os

python_global_call = 'python'

# python_global_call = 'python3'
os.system(f'{python_global_call} GTFS_wrapper.py')
os.system(f'{python_global_call} build_transfer_file.py')
os.system(f'{python_global_call} build_TBTR_dict.py')
os.system(f'{python_global_call} build_transfer_patterns.py')
os.system(f'{python_global_call} query_file.py')