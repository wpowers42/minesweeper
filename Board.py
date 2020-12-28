import numpy as np
import itertools

TYPES = {
	'U'	: -2,
	'M'	: -1,
	'C'	:  0,
	'1'	:  1,
	'2'	:  2,
	'3'	:  3,
	'4'	:  4,
	'5'	:  5,
	'6'	:  6,
	'7'	:  7,
	'8'	:  8,
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
		self.board = np.full((self._rows, self._columns), TYPES['C'], dtype=np.dtype(int))

	def _create_player_board(self):
		"""
		Creates a board of rows by columns dimensions, all set to ' '
		"""
		self.player_board = np.full((self._rows, self._columns), TYPES['C'], dtype=np.dtype(int))

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

	def reveal_tile(self, row, column):
		"""
		Reveals a tile on the Minesweeper player board.
		"""
		tile_value = self.board[(row, column)]
		if tile_value == TYPES['C']:
			self.propogate_uncovered(row, column)
		else:
			self.player_board[(row, column)] = tile_value
		self.show_player_board()
		probs = self.calculate_probabilities()
		print(probs)

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

	def calculate_probabilities(self):
		# baseline can be overruled by local baseline in either direction
		# local baselines can overrule local baseline only in greater direction
		baseline = round(self._remaining_mines / np.count_nonzero(self.player_board == TYPES['C']), 3)
		probs = np.full((self._rows, self._columns), baseline, dtype=np.dtype(float))
		for row in range(0, self._rows, 1):
			for column in range(0, self._columns, 1):
				# check if tile has value greater than covered tile and update neighbor probs.
				local_value = self.player_board[(row, column)]
				if local_value == TYPES['U']:
					probs[(row, column)] = 0
				if local_value == TYPES['C']:
					pass
					# probs[(row, column)] = np.nanmax([baseline, probs[(row, column)]])
				elif local_value > TYPES['C']:
					probs[(row, column)] = 0
					neighbor_coordinates = self._get_neighbor_coordinates(row, column)
					neighbor_values = self._get_neighbor_values(self.player_board, neighbor_coordinates)
					covered_tiles = np.count_nonzero(neighbor_values == TYPES['C'])
					local_baseline = round(local_value / covered_tiles, 3)
					for ix, value in enumerate(neighbor_values):
						if value == TYPES['C']:
							coordinates = neighbor_coordinates[ix]
							if probs[coordinates] == baseline:
								probs[coordinates] = local_baseline
								print(coordinates, local_baseline)
							else:
								probs[coordinates] = np.nanmax([local_baseline, probs[coordinates]])
		return probs


	def show_board(self):
		"""
		Prints a representation of the Minesweeper board.
		"""
		print('\n')
		for row in self.board:
			print([ REVERSE_TYPES[str(c)] for c in row ])

	def show_player_board(self):
		"""
		Prints a representation of the Minesweeper player board.
		"""
		print('\n')
		for row in self.player_board:
			print([ REVERSE_TYPES[str(c)] for c in row ])


board = Board(12, 12, 36)
board.show_board()
# board.show_player_board()
print(board.board)
board.reveal_tile(1,1)
print(board.player_board)


# TODO: how do we dynamically update probabilities, specifically the baseline?



















