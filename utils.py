import itertools
import numpy as np

"""
COORDINATES
"""

def unique_vector_coordinates(vectors):
	"""
	:param vectors: list of vectors in the form:
		[{
			'root': (0,0)
			'vector': [(2,1),(4,3)]
			'mines': 2},
		{...}]
	:return:  unique set of vectors in the form { (2,1),(4,3),.. }
	"""
	all_vectors = []
	for v in vectors:
		all_vectors = all_vectors + v['vector']
	return sorted(list(set(all_vectors)))


def non_vector_coordinates(vector_coordinates, board_coordinates, board):
	"""
	:param vector_coordinates: set of tuples in the form {(1,2),(2,3),...}
	:param board_coordinates: set of tuples in the form {(1,2),(2,3),...}
	:param board: numpy array in the form [['M','C','1',...,'X'],[...]]
	:return: set of tuples in the form {(1,2),(2,3)}
	"""
	nvc = set()
	for coord in board_coordinates:
		if coord not in vector_coordinates and board[(coord)] == 'C':
			nvc.add(coord)
	return nvc

def coordinates(rows, columns):
	"""
	Generates all possible coordinate positions for a grid of size row
	x columns.
	:param rows: integer
	:param columns: integer
	:return: set of tuples in the form {(1,2),(2,3)}
	"""
	return set(list(itertools.product(range(0, rows, 1), range(0, columns, 1))))

def neighbor_coordinates(row, column, board):
	"""
	Return all neighbor coordinates.
	:param row: integer
	:param column: integer
	:param board: numpy array in the form [['M','C','1',...,'X'],[...]]
	:return: set of tuples in the form {(1,2),(2,3)}
	"""
	rows, columns = board.shape
	neighbors = []
	for row2 in range(row-1, row+2):
		for column2 in range(column-1, column+2):
			# make sure provided coordinates are within the grid
			if (-1 < row < rows and -1 < column < columns):
				# make sure we stay within the boundaries of the grid
				if (0 <= row2 < rows) and (0 <= column2 < columns):
					# don't use self as a neighbor
					if (row != row2 or column != column2):
						neighbors.append((row2, column2))
	return set(neighbors)


"""
VALUES
"""

def sum_value_from_tuple_ndarray(tuple_ndarray):
	"""
	:param tuple_ndarray: ndarray in the form [[(0,0), 0], [(1,2), 1], ...]
	:return: integer in the form 1
	"""
	return sum([ t[1] for t in tuple_ndarray])


"""
VALIDATION
"""
def check_scenario(vectors, uvc, blacklist, remaining_mines, remaining_tiles, s):
	# we want to skip any scenarios that don't assume a mine
			# on a tile that already has a mine
	if sum(s) > remaining_mines:
		return None
	scenario = zip(uvc,s)
	for tile in scenario:
		if (tile[0] in blacklist) & (tile[1] == 0):
			return None
		
	valid = is_valid_state(vectors, scenario, remaining_mines, remaining_tiles)

	if valid:
		print(scenario)
		return scenario
	else:
		return None


def is_valid_state(vectors, scenario, remaining_mines, remaining_tiles):
	# if np.random.rand() < 0.001:
	# 	print('Vectors', vectors)
	# 	print('scenario', scenario)
	# 	print('mines and tiles', remaining_mines, remaining_tiles)

	scenario_mines = sum([ s[1] for s in scenario ])
	if scenario_mines > remaining_mines:
		return False
	# invalid scenario if all remaining tiles must be mines, but the scenario
	# doesn't place all mines
	if (remaining_tiles == remaining_mines != scenario_mines):
		return False

	# invalid scenario if we don't satify a given vectors condition (e.g. number
	# of mines place)
	for vector in vectors:
		coords = vector['vector']
		vector_mines = sum([ s[1] for s in scenario if s[0] in coords ])
		if vector['mines'] != vector_mines:
			return False

	# invalid scenario if the (remaining tiles - tiles in scenario) is less than
	# the (remaining mines - mines in scenario)
	scenario_tiles = len(scenario)
	if ((remaining_tiles - scenario_tiles) < (remaining_mines - scenario_mines)):
		return False

	# scenario has passed all checks
	return True






