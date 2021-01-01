import numpy as np
import itertools
from datetime import datetime

from video import Screen
from utils import unique_vector_coordinates, non_vector_coordinates
from utils_board import example_board

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
	def __init__(self, rows, columns, mines, debug=False):
		"""
		Initiates board of size rows by columns, with mines
		"""
		self.debug = debug
		self.rows = rows
		self.columns = columns
		self.mines = mines
		self.remaining_tiles = rows * columns
		self.remaining_mines = mines
		self.screen = Screen(rows, columns, debug)
		
		if debug:
			self.board = np.array(example_board)
			self.process_board()
		else:
			self.board = None
			self.capture()

	def capture(self):
		while True:
			capturing = self.screen.capture()
			if not capturing:
				break
			
			if self.screen.processing:
				self.screen.process()
				self.board = self.screen.board
				self.process_board()

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
		self.remaining_tiles = sum(sum( self.board == 'C' ))
		self.remaining_mines = self.mines - sum([ sum(r == 'M') for r in self.board ])
		if (self.remaining_tiles == 0):
			print('Game Complete!')
			return False
		if not self.create_vectors():
			self.probabilities()
		if self.debug:
			self.screen.print_board(self.remaining_tiles, self.remaining_mines, self.board)	
		else:
			self.screen.print_board(self.remaining_tiles, self.remaining_mines)

	
	def _non_numerical_types(self):
		return np.array([TYPES['U'],TYPES['M'],TYPES['C']])

	def create_vectors(self):
		numbered_locations = np.transpose(np.isin(self.board, self._non_numerical_types(), invert=True).nonzero())
		vectors = []
		for location in numbered_locations:
			
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
			
			print(neighbor_coordinates)
			vectors.append({
				'root': location,
				'vector': neighbor_coordinates,
			 	'mines': mines
			})

		self.vectors = vectors
		print('Vectors', vectors)
		targets = []
		mines = []
		for vector in vectors:
			if vector['mines'] == 0:
				targets = targets + vector['vector']
			if vector['mines'] == len(vector['vector']) / 2:
				mines = mines + vector['vector']

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
			print('Should skip probs...')
			return True
		return False

	def possible_states(self):
		print('Generating Possible States...')
		uvc = unique_vector_coordinates(self.vectors)
		print(uvc)
		scenarios = np.array(list(itertools.product([0,1], repeat=len(uvc))))
		states = []
		blacklist = np.transpose((self.board == 'M').nonzero())
		blacklist = set([ tuple(b) for b in blacklist ])
		for s in scenarios:
			# we want to skip any scenarios that don't assume a mine
			# on a tile that already has a mine
			scenario = list(zip(uvc,s))
			skipping = False
			for tile in scenario:
				if (tile[0] in blacklist) & (tile[1] == 0):
					skipping = True
					continue

			if not skipping:
				states.append(scenario)
		return np.array(states)

	def is_valid_state(self, scenario):

		scenario_mines = sum([ s[1] for s in scenario ])
		if scenario_mines > self.remaining_mines:
			return False
		# invalid scenario if all remaining tiles must be mines, but the scenario
		# doesn't place all mines
		if (self.remaining_tiles == self.remaining_mines != scenario_mines):
			return False

		# invalid scenario if we don't satify a given vectors condition (e.g. number
		# of mines place)
		for vector in self.vectors:
			coords = vector['vector']
			vector_mines = sum([ s[1] for s in scenario if s[0] in coords ])
			if vector['mines'] != vector_mines:
				return False

		# scenario has passed all checks
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

	def average_number_of_mines(self, states):
		mines = 0
		for state in states:
			mines += sum(state.values())
		return mines / len(states)

	def aggregate_states(self, states):
		"""
		:states: list of states in the form 
		"""
		pass

	def probabilities(self):
		states = self.valid_states()

		# sum up the number of times a mine occurs on a given cell
		# in all scenarios
		vector_cells = {}
		for state in states:
			for cell in state:
				coordinates, mines = cell
				vector_cells[coordinates] = vector_cells.get(coordinates, 0) + mines

		print(vector_cells)
		# how many mines in above, on average?
		avg_mines = self.average_number_of_mines(states)
		print(avg_mines)
		other_mines = self.remaining_mines - avg_mines
		print(other_mines)
		for k in vector_cells.keys():
			vector_cells[k] = vector_cells[k] / len(states)
		print('\nVector Cells:')
		for k in sorted(vector_cells.keys()):
			print(f"{k}: {vector_cells[k]}")
		
		nvc = self.get_non_vector_cells(vector_cells)
		for k in nvc.keys():
			vector_cells[k] = round(other_mines / len(nvc), 4)
		print('\nAll Cells:')
		for k in sorted(vector_cells.keys()):
			print(f"{k}: {vector_cells[k]}")
		probabilities = vector_cells
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

board = Board(9,9,35,debug=True)
# board = Board(9, 9, 35)
# board = Board(16, 30, 170)

# TODO: fix remaining calc?