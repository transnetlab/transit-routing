"""
CiSTUP Internship: Round 1
WARNING: DO NOT CHANGE THIS FILE.
"""
from time import time


def evaluate_Q1(sample_input1):
    marks = 0
    avg_runtime = 1
    graph_object = None
    try:
        from Q1 import Dij_generator, Q1_dijkstra
        graph_object = Dij_generator()
        start_time = time()
        candidate_output = [round(Q1_dijkstra(source, destination, graph_object)) for source, destination in sample_input1]
        avg_runtime = avg_runtime + (time() - start_time) / len(sample_input1)
        if candidate_output == output_Q1Q2:
            marks = marksQ1
    except:
        pass
    return marks, graph_object, avg_runtime


def evaluate_Q2(sample_input1, graph_object):
    marks = 0
    try:
        from Q2 import bidirectional_dij
        candidate_output = [round(bidirectional_dij(source, destination, graph_object)) for source, destination in sample_input1]
        if candidate_output == output_Q1Q2:
            marks = marksQ3
    except:
        pass
    return marks


def evaluate_Q3(input_Q3):
    marks = 0
    try:
        from Q3 import number_of_routes
        for source_id, destination_id in input_Q3:
            number_of_routes(source_id, destination_id)
        candidate_output = [number_of_routes(source_id, destination_id) for source_id, destination_id in input_Q3]
        if candidate_output == output3:
            marks = marksQ3
    except:
        pass
    return marks


def main():
    print("Running Q1")
    marksQ1, graph_object, avg_runtime = evaluate_Q1(input_Q1Q2)
    print("Running Q2")
    marksQ2 = evaluate_Q2(input_Q1Q2, graph_object)
    print("Running Q3")
    marksQ3 = evaluate_Q3(input_Q3)
    total = marksQ1 + marksQ2 + marksQ3
    print(f"Marks in Q1: {marksQ1}")
    print(f"Marks in Q2: {marksQ2}")
    print(f"Marks in Q3: {marksQ3}")
    print(f"Avg Runtime in seconds for Q1: {avg_runtime}")
    print(f"Final Score: {total}")
    return marksQ1, marksQ2, marksQ3, total, avg_runtime


if __name__ == "__main__":
    input_Q1Q2 = [(253, 127), (139, 305), (148, 99), (363, 134), (778, 396), (650, 759), (724, 547), (788, 412), (105, 1)]
    output_Q1Q2 = [38, 59, 29, 76, 30, 70, 53, 59, 51]
    input_Q3 = [('3003', '3004'), ('15', '6476b50b-bb5e-48e0-b2d9-e25aead5e3fd'), ('7', '8'), ('7', '80'), ('19', '3010'),
                ('3895ff8a-6cc3-44af-a8b5-23636fd1dba6', 'a7274768-ade1-4b21-b3b6-7f368d2a684b')]
    output3 = [2, 1, 0, 0, 1, 1]
    marksQ1, marksQ2, marksQ3 = 2, 4, 4
    main()
