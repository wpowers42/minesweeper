import time

import cv2
import mss
import numpy as np

from datetime import datetime
import pyautogui
from collections import Counter
import imutils
import os

pyautogui.FAILSAFE = True

class Screen:
	def __init__(self, rows, columns, debug):
		self.debug = debug
		self.rows = rows
		self.columns = columns
		self.top = 600
		self.left = 600
		self.height = 800
		self.width = int(self.height * (columns / rows))
		self.board = None
		self.board_raw = None
		self.processing = False
		self.mon = { "top": self.top,
					 "left": self.left,
					 "width": self.width, 
					 "height": self.height}
		self.sct = mss.mss()
		self.title = 'Minesweeper'


	def capture(self):
		img = self.sct.grab(self.mon)
		self.board_raw = np.asarray(img)

		cv2.imshow(self.title, self.board_raw)
		if cv2.waitKey(25) & 0xFF == ord("q"): 
			cv2.destroyAllWindows()
			return False
		if cv2.waitKey(25) & 0xFF == ord("s"):
			print("Processing Started")
			self.processing = True
		if cv2.waitKey(25) & 0xFF == ord("t"):
			print("Processing Stopped")
			self.processing = False
		return True


	def process(self):

		self.board = []
		for row in np.array_split(self.board_raw, self.rows, axis=0):
			row_tiles = []
			for cell in np.array_split(row, self.columns, axis=1):
				# vertical line centered
				y,x,c = cell.shape
				startx = x//2
				middle = []
				for row in cell:
					middle.append(row[startx])
				tile = self.classify_cell(np.array(middle))
				row_tiles.append(tile)
			self.board.append(row_tiles)
		self.board = np.array(self.board)
		# self.print_board(20,20)

	def get_tile_coordinate(self, row, column):
		cell_width = int(self.width / self.columns)
		left = int(column * cell_width + cell_width / 2) + self.left
		top = int(row * cell_width + cell_width / 2) + self.top
		# pyautogui.moveTo(left, top)
		# self.left_click(left, top)
		return (left, top)

	def click_to_activate(self):
		buf = 50
		pyautogui.click(x=self.left+self.width+buf, y=self.top-buf)

	def left_click(self, left, top):
		if self.debug:
			print('Simulated click at', (left, top))
			pass
		else:
			self.click_to_activate()
			pyautogui.click(x=left, y=top)

	def right_click(self, left, top):
		if self.debug:
			print('Simulated click at', (left, top))
			pass
		else:
			self.click_to_activate()
			pyautogui.click(button='right', x=left, y=top)

	def print_board(self, tiles, mines, board=[]):
		"""
		Prints a representation of the Minesweeper board.
		"""
		os.system('clear')
		print('\nBoard:')
		if len(board) == 0:
			board = self.board

		for row in board:
			print(' '.join(row))
		print(f'Remaining Tiles:{tiles}, Remaining Mines: {mines}')

	def classify_cell(self, cell):

		# bgr
		colors = {
			'C': '[229 229 229]',
			'U': '[218 218 218]',
			'1': '[255   0   0]',
			'2': '[  0 128   0]',
			'3': '[  0   0 255]',
			'4': '[128   0   0]',
			'5': '[  0   0 128]',
			'6': '[128 128   0]',
			'7': '[0 0 0]',
			'8': '[XXX XXX XXX]',
		}

		c = {}
		for pixel in np.reshape(cell, (-1,4)):
			s = str(pixel[:3])
			c[s] = c.get(s, 0) + 1
		if '[153 153 153]' in c:
			del c['[153 153 153]']
		if '[255 255 255]' in c:
			del c['[255 255 255]']
		k = Counter(c)
		high = k.most_common(4)
		top = {}
		for h in high:
			top[h[0]] = round(h[1] / (cell.size / 4),4)
		# print(top)
		if colors['3'] in top and colors['7'] in top and top[colors['7']] >= 0.050:
			return 'M'
		if colors['1'] in top and top[colors['1']] >= 0.050:
			return '1'
		elif colors['2'] in top and top[colors['2']] >= 0.075:
			return '2'
		elif colors['3'] in top and top[colors['3']] >= 0.075:
			return '3'
		elif colors['4'] in top and top[colors['4']] >= 0.075:
			return '4'
		elif colors['5'] in top and top[colors['5']] >= 0.075:
			return '5'
		elif colors['6'] in top and top[colors['6']] >= 0.075:
			return '6'
		elif colors['7'] in top and top[colors['7']] >= 0.075:
			return '7'
		elif colors['8'] in top and top[colors['8']] >= 0.075:
			return '8'
		elif colors['U'] in top and top[colors['U']] >= 0.50:
			return 'U'
		elif colors['C'] in top and top[colors['C']] >= 0.45:
			return 'C'
		else:
			return 'X'


# screen = Screen(9, 9)