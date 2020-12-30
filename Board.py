import numpy as np
import itertools

TYPES = {
	'U'	: 'U',
	'M'	: 'M',
	'C'	: 'C',
	'0'	: '0',
	'1'	: '1',
	'2'	: '2',
	'3'	: '3',
	'4'	: '4',
	'5'	: '5',
	'6'	: '6',
	'7'	: '7',
	'8'	: '8',
}

REVERSE_TYPES = {str(v): k for k, v in TYPES.items()}

class Board:
	"""
	A representation of a Minesweeper board.
	"""
	def __init__(self, rows, columns, mines):
		"""
		Initiates board of size rows by columns, with mines
		"""
		self._rows = rows
		self._columns = columns
		self._mines = mines
		self._remaining_mines = mines
		self._create_board()
		self._create_player_board()
		self._place_mines()
		self._place_numbers()

	def _create_board(self):
		"""
		Creates a board of rows by columns dimensions, all set to ' '
		"""
		self.board = np.full((self._rows, self._columns), TYPES['C'], dtype=np.dtype(str))

	def _create_player_board(self):
		"""
		Creates a board of rows by columns dimensions, all set to ' '
		"""
		self.player_board = np.full((self._rows, self._columns), TYPES['C'], dtype=np.dtype(str))

	def _coordinates(self):
		"""
		Generates all possible coordinate positions.
		"""
		return list(itertools.product(range(0, self._rows, 1), range(0, self._columns, 1)))

	def _place_mines(self):
		"""
		Randomly, non-replaceably, selects coordinates to place the mines, which
		are represented as True in a grid of False.
		"""
		rng = np.random.default_rng()
		locs = rng.choice(self._coordinates(), self._mines, replace=False)
		for loc in locs:
			self.board[loc[0]][loc[1]] = TYPES['M']

	def _place_numbers(self):
		"""
		Places numbers on the board that represent the number of adjacent cells
		containing mines.
		"""
		for row in range(0, self._rows, 1):
			for column in range(0, self._columns, 1):
				# Skip if current cell has a mine
				if (not(self.board[(row, column)] == TYPES['M'])):
					neighbor_coordinates = self._get_neighbor_coordinates(row, column)
					neighbor_values = self._get_neighbor_values(self.board, neighbor_coordinates)
					number_of_mines = np.count_nonzero(neighbor_values == TYPES['M'])
					# Set value of current tile to number of mines in neighbor cells
					cell_value = TYPES[str(number_of_mines)] if number_of_mines > 0 else TYPES['C']
					self.board[(row, column)] = cell_value

	def _get_neighbor_coordinates(self, row, column):
		"""
		Return all neighbor coordinates.
		"""
		rows, columns = self.board.shape
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
		return neighbors

	def _get_neighbor_values(self, board, neighbors):
		"""
		Return value of neighbors.
		"""
		return np.array([board[(coordinate)] for coordinate in neighbors])

	def _str2int(self, str):
		"""
		Converts a string to an int if possible, returns None otherwise
		"""
		try:
			return int(str)
		except ValueError:
			return None

	def reveal_tile(self, row, column):
		"""
		Reveals a tile on the Minesweeper player board.
		"""
		tile_value = self.board[(row, column)]
		if tile_value == TYPES['M']:
			print('GAME OVER!')
			self.show_player_board()
			return False
		elif tile_value == TYPES['C']:
			self.propogate_uncovered(row, column)
		else:
			self.player_board[(row, column)] = tile_value
		self.create_vectors()
		self.show_player_board()
		self.probabilities()

	def propogate_uncovered(self, row, column):
		"""
		Recursively checks self and neighbors for covered empty tiles.
		"""
		# return if already uncovered tile
		if self.player_board[(row, column)] != TYPES['C']:
			return
		# return if tile is not empty
		if self.board[(row, column)] != TYPES['C']:
			return
		# uncover empty tile on player board
		self.player_board[(row, column)] = TYPES['U']
		neighbors = self._get_neighbor_coordinates(row, column)
		for neighbor in neighbors:
			self.propogate_uncovered(*neighbor)

	def _non_numerical_types(self):
		return np.array([TYPES['U'],TYPES['M'],TYPES['C']])

	def create_vectors(self):
		numbered_locations = np.transpose(np.isin(self.player_board, self._non_numerical_types(), invert=True).nonzero())
		print("Numbered Locations: ", numbered_locations)
		vectors = {}
		for location in numbered_locations:
			root = ''.join([ str(i) for i in location])
			mines = self.player_board[tuple(location)]
			neighbor_coordinates = self._get_neighbor_coordinates(*location)
			neighbor_values = self._get_neighbor_values(self.player_board, neighbor_coordinates)
			print('-------')
			print(neighbor_values)
			valid_neighbors = []
			for ix, coord in enumerate(neighbor_coordinates):
				if neighbor_values[ix] == 'C':
					valid_neighbors.append(coord)
			neighbor_coordinates = valid_neighbors
			vector = ''.join([ str(c) for s in neighbor_coordinates for c in s  ])
			vectors[root] = {
				'vector': vector,
			 	'mines': int(mines)
			 }
		self.vectors = vectors

	def split_vector(self, vector):
		x = []
		y = []
		for ix, c in enumerate(vector):
			if ix % 2:
				x.append(int(c))
			else:
				y.append(int(c))
		return list(zip(x,y))

	def unique_vector_coordinates(self):
		coordinates = []
		for v in self.vectors.values():
			coordinates = coordinates + self.split_vector(v['vector'])
		return set(coordinates)

	def possible_states(self):
		cells = self.unique_vector_coordinates()
		str_cells = []
		for cell in cells:
			c = ''
			for coord in cell:
				c += str(coord)
			str_cells.append(c)
		cells = str_cells
		print(cells)
		scenarios = np.array(list(itertools.product([0,1], repeat=len(cells))))
		states = []
		for s in scenarios:
			temp = list(zip(cells,s))
			temp_dict = {}
			for t in temp:
				temp_dict[t[0]] = int(t[1])
			states.append(temp_dict)
		return np.array(states)

	def is_valid_state(self, state):
		for k,v in self.vectors.items():
			coords = self.split_vector(v['vector'])
			vector_sum = 0
			for coord in coords:
				vector_sum += state["".join([ str(c) for c in coord])]
			if v['mines'] != vector_sum:
				return False
		return True

	
	def valid_states(self):
		states = self.possible_states()
		valid_states = []
		for state in states:
			if self.is_valid_state(state):
				valid_states.append(state)
		return valid_states

	def get_non_vector_cells(self, cells):
		coords = self._coordinates()
		non_vector_cells = {}
		for coord in coords:
			c = ''.join(str(c) for c in coord)
			if c not in cells.keys() and self.player_board[(coord)] == 'C':
				non_vector_cells[c] = 0
		# print('Non-Vector Cells:')
		# for k in sorted(non_vector_cells.keys()):
		# 	print(f"{k}: {non_vector_cells[k]}")
		return non_vector_cells

	def average_number_of_mines(self, states):
		mines = 0
		for state in states:
			mines += sum(state.values())
		return mines / len(states)

	def best_choice(self, probabilities):
		lowest_probability = min(probabilities.values())
		options = [ { k: v } for k,v in probabilities.items() if v == lowest_probability]
		print(options)
		rng = np.random.default_rng()
		choice = rng.choice(options)
		print(choice)
		print(probabilities)
		return choice

	def probabilities(self):
		states = self.valid_states()
		cells = {}
		for state in states:
			for k,v in state.items():
				cells[k] = cells.get(k, 0) + v
		# how many mines in above, on average?
		mines = sum(cells.values())
		avg_mines = self.average_number_of_mines(states)
		print(cells)
		print('Avg Mines:', avg_mines)
		other_mines = self._mines - avg_mines
		for k in cells.keys():
			cells[k] = cells[k] / len(states)
		print('\nVector Cells:')
		for k in sorted(cells.keys()):
			print(f"{k}: {cells[k]}")
		
		nvc = self.get_non_vector_cells(cells)
		for k in nvc.keys():
			cells[k] = round(other_mines / len(nvc), 4)
		print('\nAll Cells:')
		for k in sorted(cells.keys()):
			print(f"{k}: {cells[k]}")
		probabilities = cells
		print('best choice', self.best_choice(probabilities))



	def show_board(self):
		"""
		Prints a representation of the Minesweeper board.
		"""
		print('\nBoard:')
		for row in self.board:
			print([ REVERSE_TYPES[str(c)] for c in row ])

	def show_player_board(self):
		"""
		Prints a representation of the Minesweeper player board.
		"""
		print('\nPlayer Board')
		for row in self.player_board:
			print([ REVERSE_TYPES[str(c)] for c in row ])


board = Board(5, 5, 5)
board.show_board()
board.show_player_board()
board.reveal_tile(3,3)

# TODO: feed in pre-defined board states?



















