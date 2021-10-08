"""
This is the Main module. See use case
"""
from time import process_time as time_measure

ALGORITHM = int(input("Press 0 for RAPTOR  \nPress 1 for TBTR\n"))
print("***************")
if ALGORITHM==0:
    VARIENT = int(input("Press 0 for Standard RAPTOR\nPress 1 for rRAPTOR  \nPress 2 for One-To-Many rRAPTOR \nPress 3 for HypRAPTOR\n"))
elif ALGORITHM==1:
    VARIENT = int(input("Press 0: Standard TBTR\n Press 1: rTBTR  \nPress 2: One-To-Many rTBTR \nPress 3: HypTBTR\n"))
print("***************")
TEST_CASE = int(input("Press 0: To use test case \nPress 1: To enter values manually\n"))

if __name__ == "__main__":
    if TEST_CASE==0:
        if ALGORITHM==0:
            if VARIENT==0:
                from test_case.std_raptor_tc import *
            elif VARIENT==1:
                from test_case.rraptor_tc import *
            elif VARIENT==2:
                from test_case.one_to_many_rraptor import *
        if ALGORITHM==1:
            if VARIENT==0:
                from test_case.std_tbtr_tc import *
            elif VARIENT==1:
                pass
            elif VARIENT==2:
                pass
    elif TEST_CASE==1:
        from miscellaneous_func import *
        SOURCE, DESTINATION = input("Enter SOURCE stop-id (int)"), input("Enter SOURCE stop-id (int)")
        PRINT_PARA = input("Press 1 to print complete journey details else 0")
        WALKING_FROM_SOURCE = input("Press 1 to allow walking from SOURCE stop else 0")
        MAX_TRANSFER = input("Enter maximum transfer limit")
        CHANGE_TIME_SEC = 0
        D_TIME = input("Enter maximum transfer limit")
        check(stops_dict, stoptimes_dict, stop_times_file)
        if ALGORITHM==1:
            if VARIENT==0:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
            elif VARIENT==1:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
            elif VARIENT==2:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
            elif VARIENT==3:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
        elif ALGORITHM==0:
            if VARIENT==0:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
            elif VARIENT==1:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
            elif VARIENT==2:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
            elif VARIENT==3:
                VARIENT = input("Press 0: Standard RAPTOR\nPress 1: rRAPTOR  \nPress 2: One-To-Many rRAPTOR \nPress 3: HypRAPTOR")
