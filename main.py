"""
This is the Main module.
"""


def take_inputs():
    """
    defines the use input
    Returns:
        algorithm (int): algorithm type. 0 for RAPTOR and 1 for TBTR
        variant (int): variant of the algorithm. 0 for normal version,
                                                 1 for range version,
                                                 2 for One-To-Many version,
                                                 3 for Hyper version
    """
    algorithm = int(input("Press 0 for RAPTOR \nPress 1 for TBTR \n"))
    print("***************")
    if algorithm == 0:
        variant = int(input(
            "Press 0 for RAPTOR \nPress 1 for rRAPTOR \nPress 2 for One-To-Many rRAPTOR \nPress 3 for HypRAPTOR \n"))
    elif algorithm == 1:
        variant = int(input("Press 0: TBTR \nPress 1: rTBTR \nPress 2: One-To-Many rTBTR \nPress 3: HypTBTR \n"))
    print("***************")
    return algorithm, variant


def main():
    """
    Runs the test case depending upon the values of algorithm, variant
    """
    algorithm, variant = take_inputs()
    if algorithm == 0:
        if variant == 0:
            import test_case.std_raptor_tc
        elif variant == 1:
            import test_case.rraptor_tc
        elif variant == 2:
            import test_case.one_to_many_rraptor
        elif variant == 3:
            import test_case.hypraptor_tc
    if algorithm == 1:
        if variant == 0:
            import test_case.std_tbtr_tc
        elif variant == 1:
            import test_case.rtbtr_tc
        elif variant == 2:
            import test_case.one_to_many_rtbtr_tc
        elif variant == 3:
            import test_case.hyptbtr_tc


if __name__ == "__main__":
    main()
