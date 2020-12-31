import numpy as np
import itertools
from datetime import datetime

from ui import Screen

start = datetime.now()

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
		self.screen = Screen(rows, columns)
		self.board = self.screen.capture()
		self.rows = rows
		self.columns = columns
		self.mines = mines
		self.remaining_tiles = sum(sum( self.board == 'C' ))
		self.remaining_mines = self.mines - sum([ sum(r == 'M') for r in self.board ])

	def _coordinates(self):
		"""
		Generates all possible coordinate positions.
		"""
		return list(itertools.product(range(0, self.rows, 1), range(0, self.columns, 1)))

	
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


	def process_board(self):
		"""
		Calculates the next best move.
		"""
		if not self.create_vectors():
			self.probabilities()
		self.screen.print_board(self.remaining_tiles, self.remaining_mines)
		self.board = self.screen.capture()
		self.remaining_tiles = sum(sum( self.board == 'C' ))
		# print('Remaining Tiles:', self.remaining_tiles)
		if (self.remaining_tiles == 0):
			print('Game Complete!')
			return False
		self.remaining_mines = self.mines - sum([ sum(r == 'M') for r in self.board ])
		self.process_board()

	
	def _non_numerical_types(self):
		return np.array([TYPES['U'],TYPES['M'],TYPES['C']])

	def create_vectors(self):
		numbered_locations = np.transpose(np.isin(self.board, self._non_numerical_types(), invert=True).nonzero())
		vectors = {}
		for location in numbered_locations:
			root = ''.join([ str(i) for i in location])
			
			mines = int(self.board[tuple(location)])
			neighbor_coordinates = self._get_neighbor_coordinates(*location)
			neighbor_values = self._get_neighbor_values(self.board, neighbor_coordinates)
			
			valid_neighbors = []
			valid_neighbor_values = []
			for ix, coord in enumerate(neighbor_coordinates):
				if neighbor_values[ix] == 'M':
					mines = mines - 1
				elif neighbor_values[ix] == 'C':
					valid_neighbors.append(coord)
					valid_neighbor_values.append(neighbor_values[ix])
			
			neighbor_coordinates = valid_neighbors
			neighbor_values = np.array(valid_neighbor_values)

			if len(neighbor_coordinates) == 0:
				continue
			
			vector = ''.join([ str(c) for s in neighbor_coordinates for c in s  ])
			vectors[root] = {
				'vector': vector,
			 	'mines': mines
			}

			# if (mines == len(neighbor_coordinates)):
			# 	# print('100% Mines Found', root, vectors[root])
			# 	for v in self.split_vector(vectors[root]['vector']):
			# 		cor = self.screen.get_tile_coordinate(*tuple(v))
			# 		self.screen.right_click(*cor)

			# 	return True
		self.vectors = vectors
		targets = []
		mines = []
		for k,v in self.vectors.items():
			if v['mines'] == 0:
				targets = targets + self.split_vector(v['vector'])
			if v['mines'] == len(v['vector']) / 2:
				print(v['vector'], v['mines'])
				mines = mines + self.split_vector(v['vector'])

		targets = set(targets)
		mines = set(mines)
		if len(targets) > 0:
			for target in targets:
				cor = self.screen.get_tile_coordinate(*target)
				self.screen.left_click(*cor)
		if len(mines) > 0:
			for mine in mines:
				cor = self.screen.get_tile_coordinate(*mine)
				self.screen.right_click(*cor)

		if len(targets) > 0 or len(mines) > 0:
			return True
		return False

	def split_vector(self, vector):
		x = []
		y = []
		for ix, c in enumerate(vector):
			if ix % 2:
				x.append(int(c))
			else:
				y.append(int(c))
		s = list(zip(y,x))
		return s

	def unique_vector_coordinates(self):
		coordinates = []
		for v in self.vectors.values():
			coordinates = coordinates + self.split_vector(v['vector'])
		return set(coordinates)

	def possible_states(self):
		print('Generating Possible States...')
		cells = self.unique_vector_coordinates()
		str_cells = []
		for cell in cells:
			c = ''
			for coord in cell:
				c += str(coord)
			str_cells.append(c)
		cells = str_cells
		scenarios = np.array(list(itertools.product([0,1], repeat=len(cells))))
		states = []
		blacklist = np.transpose((self.board == 'M').nonzero())
		blacklist = [ ''.join([str(c) for c in b]) for b in blacklist ]
		blacklist = set(blacklist)
		for s in scenarios:
			temp = list(zip(cells,s))
			temp_dict = {}
			passing = False
			for t in temp:
				temp_dict[t[0]] = int(t[1])
				if t[0] in blacklist and int(t[1]) == 0:
					passing = True
					continue
			if not passing:
				states.append(temp_dict)
		return np.array(states)

	def is_valid_state(self, state):
		if sum(state.values()) > self.remaining_mines:
			return False
		if self.remaining_tiles == len(state) and self.remaining_mines != sum(state.values()):
			return False
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
		for s in valid_states:
			print(s)
		return valid_states

	def get_non_vector_cells(self, cells):
		coords = self._coordinates()
		non_vector_cells = {}
		for coord in coords:
			c = ''.join(str(c) for c in coord)
			if c not in cells.keys() and self.board[(coord)] == 'C':
				non_vector_cells[c] = 0
		return non_vector_cells

	def average_number_of_mines(self, states):
		mines = 0
		for state in states:
			mines += sum(state.values())
		return mines / len(states)

	def probabilities(self):
		states = self.valid_states()
		cells = {}
		for state in states:
			for k,v in state.items():
				cells[k] = cells.get(k, 0) + v
		# how many mines in above, on average?
		avg_mines = self.average_number_of_mines(states)
		print(avg_mines)
		other_mines = self.remaining_mines - avg_mines
		print(other_mines)
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
		clean = []
		mines = []
		for k,v in probabilities.items():
			k = tuple([int(c) for c in str(k)])
			k = self.screen.get_tile_coordinate(*k)
			if v == 0:
				clean.append(k)
			if v == 1:
				mines.append(k)

		if len(clean):
			for c in clean:
				self.screen.left_click(*c)
		if len(mines):
			for m in mines:
				self.screen.right_click(*m)
		if len(clean) or len(mines):
			return True
		else:
			lowest_probability = min(probabilities.values())
			options = [ { k: v } for k,v in probabilities.items() if v == lowest_probability]
			rng = np.random.default_rng()
			choice = rng.choice(options)
			cor = tuple([ int(char) for char in choice[0] ])
			cor = self.screen.get_tile_coordinate(*cor)
			self.screen.left_click(*cor)
			return True




# https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#9x9n35#952602088781240
# examine: https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#9x9n35#111486851880096


board = Board(9, 9, 35)
board.process_board()

# TODO: fix remaining calc?