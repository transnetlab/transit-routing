"""
This is the Main module. See use case
"""

def take_inputs():
    """
    defines the use input
    Returns:
        ALGORITHM (int): algorithm type. 0 for RAPTOR and 1 for TBTR
        VARIANT (int): variant of the algorithm. 0 for normal version, 1 for range version, 2 for One-To-Many version, 3 for Hyper version
    """
    ALGORITHM = int(input("Press 0 for RAPTOR  \nPress 1 for TBTR\n"))
    print("***************")
    if ALGORITHM==0:
        VARIANT = int(input("Press 0 for Standard RAPTOR\nPress 1 for rRAPTOR  \nPress 2 for One-To-Many rRAPTOR \nPress 3 for HypRAPTOR\n"))
    elif ALGORITHM==1:
        VARIANT = int(input("Press 0: Standard TBTR\n Press 1: rTBTR  \nPress 2: One-To-Many rTBTR \nPress 3: HypTBTR\n"))
    print("***************")
    return ALGORITHM, VARIANT

def main():
    """
    Runs the test case depending upon the values of ALGORITHM, VARIANT
    Args:
    Returns: None
    """
    ALGORITHM, VARIANT = take_inputs()
    if ALGORITHM==0:
        if VARIANT==0:
            import test_case.std_raptor_tc
        elif VARIANT==1:
            import test_case.rraptor_tc
        elif VARIANT==2:
            import test_case.one_to_many_rraptor
        elif VARIANT==3:
            import test_case.hypraptor_tc
    if ALGORITHM==1:
        if VARIANT==0:
            import test_case.std_tbtr_tc
        elif VARIANT==1:
            import test_case.rraptor_tc
        elif VARIANT==2:
            import test_case.one_to_many_rtbtr_tc
        elif VARIANT==3:
            import test_case.hyptbtr_tc

if __name__ == "__main__":
    main()
