import time
import itertools
import numpy as np
import multiprocessing as mp
from functools import partial

from video import Screen
from utils import unique_vector_coordinates, non_vector_coordinates
from utils import sum_value_from_tuple_ndarray, coordinates, neighbor_coordinates
from utils import is_valid_state, check_scenario
from utils_board import example_board

from logic import Solver

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
		if (self.remaining_mines == 0):
			# self.print_board()
			self.click_remaining_tiles()
			print('Game Complete!')
			return False
		if not self.create_vectors():
			self.probabilities()
		# self.print_board()
		return True

	def click_remaining_tiles(self):
		"""
		This is triggered when no mines are left on the board, so it's safe to click the
		remaining tiles.
		"""
		safe = np.transpose((self.board == 'C').nonzero())
		safe = [ self.screen.get_tile_coordinate(c) for c in safe ]
		list(itertools.starmap(self.screen.left_click, safe))
	
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
			
			if tuple(location) == (4,17):
				print (location, nc, mines)

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
				cor = self.screen.get_tile_coordinate(target)
				self.screen.left_click(*cor)
		
		# mark any mine tiles
		if len(mines) > 0:
			for mine in mines:
				cor = self.screen.get_tile_coordinate(mine)
				self.screen.right_click(*cor)

		# if we clicked or marked any tiles, skip the final probability step
		if len(targets) > 0 or len(mines) > 0:
			return True
		
		# if no safe or mine tiles discovered, continue to the final probability step
		return self.probabilities()


	def average_number_of_mines(self, states):
		mines = 0
		for state in states:
			mines += sum_value_from_tuple_ndarray(state)
		return mines / len(states)

	def probabilities(self):
		solution = self.solve()

		list(itertools.starmap(self.screen.left_click, solution['safe']))
		list(itertools.starmap(self.screen.right_click, solution['mines']))

		if (len(solution['safe']) > 0) or (len(solution['mines']) > 0):
			return True
		elif (len(solution['alternative']) > 0):
			print('Taking an educated guess!')
			self.screen.left_click(*solution['alternative'])
			return True
		else:
			print('Unable to find match.')
			return False


	def solve(self):
		solver = Solver(self.vectors)
		solution = solver.solutions()
		print(solution)
		safe = [ self.screen.get_tile_coordinate(k) for k,v in solution.items() if v == 0.0 ]
		mines = [ self.screen.get_tile_coordinate(k) for k,v in solution.items() if v == 1.0 ]

		# get they keys of the items with the lowest values and select a random one
		rng = np.random.default_rng()
		minval = min(solution.values()) if len(solution.values()) > 0 else 0
		if minval != 0:
			alternative = self.screen.get_tile_coordinate(rng.choice(list(filter(lambda x: solution[x]==minval, solution))))
		else:
			alternative = ()

		result = {
			'safe': safe,
			'mines': mines,
			'alternative': alternative
		}

		return result


# https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#9x9n35#952602088781240
# examine: https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#9x9n35#111486851880096
if __name__ == "__main__":
	board = Board(16,30,170,debug=False)