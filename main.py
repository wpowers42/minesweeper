import itertools
import numpy as np
from datetime import datetime

from video import Screen
from utils import unique_vector_coordinates, non_vector_coordinates
from utils import sum_value_from_tuple_ndarray, coordinates, neighbor_coordinates
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
				self.print_board()
				if not self.process_board():
					break

	def _get_neighbor_values(self, board, neighbors):
		"""
		Return value of neighbors.
		"""
		return np.array([board[(coordinate)] for coordinate in neighbors])

	def print_board(self):
		"""
		Prints a representation of the board.
		"""
		if self.debug:
			self.screen.print_board(self.remaining_tiles, self.remaining_mines, self.board)	
		else:
			self.screen.print_board(self.remaining_tiles, self.remaining_mines)

	def process_board(self):
		"""
		Calculates the next best move.
		"""
		self.remaining_tiles = sum(sum( self.board == 'C' ))
		self.remaining_mines = self.mines - sum([ sum(r == 'M') for r in self.board ])
		if (self.remaining_tiles == 0):
			# self.print_board()
			print('Game Complete!')
			return False
		if not self.create_vectors():
			self.probabilities()
		# self.print_board()
		return True

	
	def _non_numerical_types(self):
		return np.array([TYPES['U'],TYPES['M'],TYPES['C']])

	def create_vectors(self):
		numbered_locations = np.transpose(np.isin(self.board, self._non_numerical_types(), invert=True).nonzero())
		vectors = []
		for location in numbered_locations:
			
			mines = int(self.board[tuple(location)])
			nc = neighbor_coordinates(*location, self.board)
			neighbor_values = self._get_neighbor_values(self.board, nc)
			
			valid_neighbors = []
			valid_neighbor_values = []
			for ix, coord in enumerate(nc):
				if neighbor_values[ix] == 'M':
					mines = mines - 1
				elif neighbor_values[ix] == 'C':
					valid_neighbors.append(coord)
					valid_neighbor_values.append(neighbor_values[ix])
			
			nc = valid_neighbors
			neighbor_values = np.array(valid_neighbor_values)

			if len(nc) == 0:
				continue
			
			vectors.append({
				'root': location,
				'vector': nc,
			 	'mines': mines
			})

		self.vectors = vectors
		targets = []
		mines = []
		for vector in vectors:
			# if the remaining mines in the vector is 0, all tiles are safe
			# if the remaining mines in the vector equals the remaining tiles,
			# all tiles are mines
			if vector['mines'] == 0:
				targets = targets + vector['vector']
			if vector['mines'] == len(vector['vector']):
				mines = mines + vector['vector']

		targets = set(targets)
		mines = set(mines)

		# click on any safe tiles
		if len(targets) > 0:
			for target in targets:
				cor = self.screen.get_tile_coordinate(*target)
				self.screen.left_click(*cor)
		
		# mark any mine tiles
		if len(mines) > 0:
			for mine in mines:
				cor = self.screen.get_tile_coordinate(*mine)
				self.screen.right_click(*cor)

		# if we clicked or marked any tiles, skip the final probability step
		if len(targets) > 0 or len(mines) > 0:
			return True

		# if no safe or mine tiles discovered, continue to the final probability step
		return False

	def possible_states(self):
		print('Generating Possible States...')
		uvc = unique_vector_coordinates(self.vectors)
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
		return np.array(states, dtype=object)

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

		# invalid scenario if the (remaining tiles - tiles in scenario) is less than
		# the (remaining mines - mines in scenario)
		scenario_tiles = len(scenario)
		if ((self.remaining_tiles - scenario_tiles) < (self.remaining_mines - scenario_mines)):
			return False

		# scenario has passed all checks
		return True

	
	def valid_states(self):
		states = self.possible_states()
		valid_states = []
		for state in states:
			if self.is_valid_state(state):
				valid_states.append(state)
		return valid_states

	def average_number_of_mines(self, states):
		mines = 0
		for state in states:
			mines += sum_value_from_tuple_ndarray(state)
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
		vc = {}
		for state in states:
			for cell in state:
				coord, mines = cell
				vc[coord] = vc.get(coord, 0) + mines

		for state in states:
			print(state)

		# how many mines in above, on average?
		avg_mines = self.average_number_of_mines(states)
		other_mines = self.remaining_mines - avg_mines

		print('Avg', avg_mines, 'Other', other_mines)
		for k in vc.keys():
			vc[k] = vc[k] / len(states)
		# print('\nVector Cells:')
		# for k in sorted(vc.keys()):
		# 	print(f"{k}: {vc[k]}")
		
		bc = coordinates(self.rows, self.columns)
		b = self.board
		nvc = non_vector_coordinates(vc, bc, b)
		for k in nvc:
			vc[k] = round(other_mines / len(nvc), 4)
		print('\nAll Cells:')
		for k in sorted(vc.keys()):
			print(f"{k}: {vc[k]}")

		probabilities = vc
		clean = []
		mines = []

		# if probability is 0, add to list of tiles to click
		# if probability is 1, add to list of tiles to mark as mine
		for k,v in probabilities.items():
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
			print("Best Tile:", choice)
			cor = list(choice.keys())[0]
			cor = self.screen.get_tile_coordinate(*cor)
			self.screen.left_click(*cor)
			return True




# https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#9x9n35#952602088781240
# examine: https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#9x9n35#111486851880096

board = Board(16,16,99,debug=False)
# board = Board(9, 9, 35)
# board = Board(16, 30, 170)

# TODO: fix remaining calc?