import unittest
from test import support
import numpy as np

# from main import Board
from utils import *

class UtilsTest(unittest.TestCase):

	def setUp(self):
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

	def test_sum_value_from_tuple_ndarray(self):
		tn = [[(1, 2), 0],
			  [(0, 0), 1],
			  [(1, 1), 0],
			  [(0, 2), 0],
			  [(1, 0), 0]]
		self.assertEqual(sum_value_from_tuple_ndarray(tn), 1)

	def test_coordinates(self):
		rows = 3
		columns = 4
		expected_result = set([(0, 0),(0, 1),(0, 2),(0, 3),
						   	   (1, 0),(1, 1),(1, 2),(1, 3),
						   	   (2, 0),(2, 1),(2, 2),(2, 3)])

		self.assertEqual(coordinates(rows, columns), expected_result )


	def test_neighbor_coordinates(self):
		row = 1
		column = 1
		board = np.array([['C','C','C','C'],
						  ['C','C','C','C'],
						  ['C','C','C','C'],
						  ['C','C','C','C']])
		expected_result = set([(0,0),(0,1),(0,2),
							   (1,0),(1,2),(2,0),
							   (2,1),(2,2)])
		self.assertEqual(neighbor_coordinates(row, column, board), expected_result)

if __name__ == '__main__':
	unittest.main(verbosity=2)