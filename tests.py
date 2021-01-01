import unittest
from test import support
import numpy as np

# from main import Board
from utils import *

class UtilsTest(unittest.TestCase):

	def setUp(self):
		# self.rows = 9
		# self.columns = 9
		# self.mines = 35
		# self.board = Board(self.rows, self.columns, self.mines)
		pass

	def tearDown(self):
		pass

	def test_unique_vector_coordinates(self):
		v = unique_vector_coordinates([
			{
				'root': (0,0),
				'vector': [(2,1),(4,3)],
				'mines': 2 
			},
			{ 
				'root': (2,2),
				'vector': [(2,1),(0,2)],
				'mines': 2 
			}])
		self.assertEqual(v, {(0,2),(2,1),(4,3)})
		self.assertEqual(v, {(2,1),(0,2),(4,3)})
		self.assertNotEqual(v, {(0,2),(2,1)})

	def test_non_vector_coordinates(self):
		vc = {(0,0),(0,1),(1,0)}
		bc = {(0,0),(0,1),(1,0),(1,1)}
		b = np.array([['1','1'],['M','C']])
		nvc = non_vector_coordinates(vc, bc, b)
		self.assertEqual(nvc, {(1,1)})

		vc.add((1,1))
		nvc = non_vector_coordinates(vc, bc, b)
		self.assertEqual(nvc, set({}))

if __name__ == '__main__':
	unittest.main(verbosity=2)