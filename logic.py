import ast
import networkx 
from networkx.algorithms.components.connected import connected_components
from constraint import *

from utils import unique_vector_coordinates

def to_graph(l):
    G = networkx.Graph()
    for part in l:
        # each sublist is a bunch of nodes
        G.add_nodes_from(part)
        # it also imlies a number of edges:
        G.add_edges_from(to_edges(part))
    return G

def to_edges(l):
    """ 
        treat `l` as a Graph and returns it's edges 
        to_edges(['a','b','c','d']) -> [(a,b), (b,c),(c,d)]
    """
    it = iter(l)
    last = next(it)

    for current in it:
        yield last, current
        last = current

class Solver:
	def __init__(self, vectors):
		self.vectors = vectors
		self.clusters = self.group_vectors()

	def solutions(self):
		"""
		For each cluster, get the solution.
		"""
		solutions = map(self.get_solution, self.clusters)
		return { k: v for s in solutions for k,v in s.items() }
		

	def get_solution(self, vectors):
		"""
		:param vectors: a list of vectors that form a cluster
		:return: a list of zero or more result dicts
		"""
		uvc = unique_vector_coordinates(vectors)
		problem = Problem()
		self.add_variables(problem, uvc)
		self.add_contraints(problem, vectors)
		return self.combine_solutions(problem.getSolutions())

	def add_variables(self, problem, variables):
		"""
		Turns all unique coordinates into a string and adds each as a variable
		to the problem.
		:return: None
		"""
		# self.uvc = unique_vector_coordinates(self.vectors)
		for v in variables:
			problem.addVariable(str(v), [0,1])
		return None

	def add_contraints(self, problem, vectors):
		"""
		Adds contraints for each vector.
		"""
		for v in vectors:
			variables = tuple([str(c) for c in v['vector']])
			problem.addConstraint(ExactSumConstraint(v['mines']), variables)

	def group_vectors(self):
		"""
		Groups vectors into clusters to improve the solving efficiency and reduce
		the complexity space.
		"""		
		uvc = unique_vector_coordinates(self.vectors)
		related = []
		for c in uvc:
			related = related + [[ tuple(v['root']) for v in self.vectors if c in v['vector'] ]]

		G = to_graph(related)
		cc = list(connected_components(G))
		clusters = []
		for c in cc:
			cluster = []
			for v in self.vectors:
				if tuple(v['root']) in c:
					cluster.append(v)
			clusters.append(cluster)
		return clusters

	def combine_solutions(self, solutions):
		"""
		Returns probabilities of each coordinate being a mine. 0 == safe, 1 == mine.
		:return: dict of floats in form { (0,0): 0.253, ... }
		"""
		result = {}
		for s in solutions:
			for k,v in s.items():
				t = ast.literal_eval(k)
				result[t] = result.get(t, 0) + v

		for key in result.keys():
			result[key] = result[key] / len(solutions)

		return result


# vectors = [{'root': [3, 2], 'vector': [(2, 1), (2, 3), (2, 2)], 'mines': 2},
# 			{'root': [3, 3], 'vector': [(2, 4), (2, 3), (2, 2)], 'mines': 1},
# 			{'root': [3, 4], 'vector': [(2, 4), (2, 3), (2, 5)], 'mines': 2},
# 			{'root': [3, 5], 'vector': [(2, 4), (2, 6), (2, 5)], 'mines': 1},
# 			{'root': [4, 6], 'vector': [(3, 7), (5, 7), (4, 7)], 'mines': 1},
# 			{'root': [5, 6], 'vector': [(5, 7), (6, 7), (4, 7)], 'mines': 1},
# 			{'root': [6, 1], 'vector': [(7, 1), (7, 0), (5, 0), (6, 0)], 'mines': 0}, 
# 			{'root': [6, 6], 'vector': [(7, 7), (5, 7), (6, 7)], 'mines': 0},
# 			{'root': [7, 5], 'vector': [(8, 6)], 'mines': 0}]

# solver = Solver(vectors)
# print(solver.get_solutions())