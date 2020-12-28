"""
- for all remaining cell, assign probability equal to remaining mines / remaining cells
- for all cells with information, do the following:
	: if cell is blank, skip
	: if cell has a number, get remaining cells around it, and assign probability equal to 
	  number / remaining cells. assign prob to cell if greater than current prob.
- for all cells with 100%:
	: mark as mine
	: reduce neighbor counts by 1
	: update probabilities until no cells have 100%
- find the cell with the lowest probability, and click it
	: if cell is blank or a number, continnue
	: if cell is a mine, end game
"""

import numpy as np
import pandas as pd

remaining_mines = 2

board = [
	[0, 0, 0, 0],
	[0, 1, 1, 1],
	[0, 2,-1, 2],
	[0, 2,-1, 2],
]

# state = [
# 	[-1, -1, -1, -1],
# 	[-1, -1, -1, -1],
# 	[-1, -1, -1, -1],
# 	[-1, -1, -1, -1],
# ]

# state = [
# 	[0, 0,  1, -1],
# 	[0, 0,  1, -1],
# 	[0, 1,  1, -1],
# 	[0, 1, -1, -1],
# ]

STATES = {
	'UNKNOWN': None,
	'MINE': -1,
	'0': 0,
	'1': 1,
	'2': 2,
	'3': 3,
	'4': 4,
}

state = [
	[0, 0,  1, -1],
	[0, 0,  1, -1],
	[0, 1,  1, 1],
	[0, 1, -1, -1],
]

def remaining_cells(state):
	return sum([c.count(-1) for c in state])

# print(remaining_cells(state))

def assign_general_probabilities(state, remaining_mines):
	cells = remaining_cells(state)
	prob = round(remaining_mines / cells, 6)
	probs = [ [ prob if col == -1 else np.NaN for col in row ] for row in state ]
	return probs

def get_neighbors(state, location):
	row, col = location
	rmax = len(state) - 1
	cmax = len(state[0]) - 1

	neighbors = []
	for c in range(-1,2,1):
		ncol = col + c
		if ncol < 0 or ncol > cmax:
			continue
		for r in range(-1,2,1):
			nrow = row + r
			# ignore self
			if c == 0 and r == 0:
				continue
			if nrow < 0 or nrow > rmax:
				continue
			# if state[nrow][ncol] == -1:
			neighbors.append([nrow, ncol])

	return neighbors

# print(get_neighbors(state, (1,1)))

def assign_local_probabilities(state, probs):
	for rix, row in enumerate(state):
		for cix, col in enumerate(row):
			if col > 0:
				neighbors = get_neighbors(state, (rix, cix))
				unknown_neighbors = []
				for n in neighbors:
					if state[n[0]][n[1]] == -1:
						unknown_neighbors.append(n)
				print(unknown_neighbors)
				mines = col
				cells = len(unknown_neighbors)
				prob = round(mines / cells, 6)
				for neighbor in unknown_neighbors:
					if probs[neighbor[0]][neighbor[1]] < prob:
						probs[neighbor[0]][neighbor[1]] = prob
					if probs[neighbor[0]][neighbor[1]] == 1:
						print(neighbor, ' has 100% prob')
						ns = get_neighbors(state, (neighbor[0], neighbor[1]))
						value_neighbors = []
						for n in ns:
							if state[n[0]][n[1]] != -1:
								value_neighbors.append(n)
						print(value_neighbors)
	return probs


def check_for_mines(state, probs):
	mines = np.where(probs == 1)


def find_best_move(probs):
	# find lowest prob
	lowest_probability = np.nanmin(probs)
	print("Lowest Prob: ", lowest_probability)
	options = np.where(probs == lowest_probability)
	options = list(zip(*options))
	# print(pd.DataFrame(options))
	# randomly pick from options
	return options[np.random.choice(len(options))]
	# return None

probs = assign_general_probabilities(state, remaining_mines)
print(pd.DataFrame(probs))

probs = assign_local_probabilities(state, probs)
print(pd.DataFrame(probs))

best_move = find_best_move(probs)
print(best_move)