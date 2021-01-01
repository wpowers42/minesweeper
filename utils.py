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