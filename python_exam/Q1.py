"""
CiSTUP Internship: Round 1
Enter the solution for Q1 here.
Note: You may use may define any additional class, functions if necessary.
However, DO NOT CHANGE THE TEMPLATE CHANGE THE TEMPLATE OF THE FUNCTIONS PROVIDED.
"""


def Dij_generator():
    """
    Reads the ChicagoSketch_net.tntp and convert it into suitable python object on which you will implement shortest-path algorithms.

    Returns:
        graph_object: variable containing network information.
    """
    graph_object = None
  
       
    class Graph():

	def __init__(source, vertices):
		source.V = vertices
		source.graph = [[0 for column in range(vertices)]
					for row in range(vertices)]

	def printSolution(source, length):
		print("Source \tDistance from Source: graph_object")
		for node in range(source.V):
			print(node, "\t", length[node])
    

    def minDistance(source, length, sptSet):        # Initialize minimum distance for next node
		min = sys.maxsize

		# Search not nearest vertex not in the
		# shortest path tree
		for u in range(source.V):
			if length[u] < min and sptSet[u] == False:
				graph_object = length[u]
			
        return graph_object


def Q1_dijkstra(source: int, destination: int, graph_object) -> int:
    """
    Dijkstra's algorithm.

    Args:
        source (int): Source stop id
        destination (int): : destination stop id
        graph_object: python object containing network information

    Returns:
        shortest_path_distance (int): length of the shortest path.

    Warnings:
        If the destination is not reachable, function returns -1
    """
    shortest_path_distance = -1
    try:
        
        def dijkstra(source, shortest_path_distance):

		length = [sys.maxsize] * source.V
		length[shortest_path_distance] = 0
		sptSet = [False] * source.V

		for cout in range(source.V):

			                                                                                    # Pick the minimum distance vertex from
		                                                                                    	# the set of vertices not yet processed.
			x = source.minDistance(length, sptSet)

			                                                                                    # Put the minimum distance vertex in the
			                                                                                    # shortest path tree
			sptSet[x] = True

			                                                                                    # Update dist value of the adjacent vertices
			                                                                                    # of the picked vertex only if the current
			                                                                                    # distance is greater than new distance and
		                                                                                     	# the vertex in not in the shortest path tree
			for y in range(source.V):
				if source.graph[x][y] > 0 and sptSet[y] == False and \
						length[y] > length[x] + source.graph[x][y]:
					length[y] = length[x] + source.graph[x][y]

		source.shortest_path_distance(length)
        return shortest_path_distance
   
