import itertools

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
	return set(all_vectors)


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