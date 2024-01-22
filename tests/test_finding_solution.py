import random
import unittest

from karnobh.crosswordist.affine_2d import (FlatMatrix, point, translate, rotate, scale, identity,
                                            WrongMatrixDimension)
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, WordDirection)
from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)
from karnobh.crosswordist.solution_finder import find_solution, find_solution2

import sys

# Set the stack size to 10000
sys.setrecursionlimit(30000)

class TestFiningSolution(unittest.TestCase):

    def test_cross_word_index_creation(self):
        grid_data = [1, 1, 0, 0, 0, 0, 1,
                     1, 0, 0, 0, 0, 0, 0,
                     1, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     1, 1, 1, 0, 0, 0, 0]
        size = 7
        grid = FlatMatrix(size, size, new_state=grid_data)
        words_layout = get_all_checked_words_layout(grid)
        print("words layout = ", words_layout)
        for j in range(grid._height):
            for i in range(grid._width):
                print(grid.get(i, j), end=" ")
            print()
        cross_words_index = create_cross_words_index(words_layout, grid)
        print(cross_words_index)
        with open('/tmp/words_tests/index.json') as f:
            wi_loaded = WordsIndex(file=f)
        print("grid: \n", grid.pretty_log({0: "_", 1: "*"}))
        sol = find_solution(word_index=wi_loaded, cross_words_index=cross_words_index,
                            orig_grid=grid)
        print(sol)

    def test_cross_word_index_creation2(self):
        grid_data = [1, 1, 0, 0, 0, 0, 1,
                     1, 0, 0, 0, 0, 0, 0,
                     1, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     1, 1, 1, 0, 0, 0, 0]
        size = 7
        grid = FlatMatrix(size, size, new_state=grid_data)
        words_layout = get_all_checked_words_layout(grid)
        print("words layout = ", words_layout)
        for j in range(grid._height):
            for i in range(grid._width):
                print(grid.get(i, j), end=" ")
            print()
        cross_words_index = create_cross_words_index(words_layout, grid)
        print(cross_words_index)
        with open('/tmp/words_tests/index.json') as f:
            wi_loaded = WordsIndex(file=f)
        print("grid: \n", grid.pretty_log({0: "_", 1: "*"}))
        sol = find_solution2(word_index=wi_loaded, cross_words_index=cross_words_index,
                             orig_grid=grid)
        print(sol)

    def test_finding_solution_with_generating(self):
        with open('/tmp/words_tests/index.json') as f:
            wi_loaded = WordsIndex(file=f)
        for num in range(1):
            if num % 10 == 0:
                # logger.info("Generated numbers = %s", num)
                print("test_finding_solution_with_generating::Generated_nums = ", num)
            grid_size = 11
            symmetry = random.choice(["X", "NO"])
            grid = create_random_grid(grid_size, symmetry="X")
            print("grid: \n", grid.pretty_log({0: "_", 1: "*"}))
            words_layout = get_all_checked_words_layout(grid)
            cross_words_index = create_cross_words_index(words_layout, grid)
            print(cross_words_index)
            sol = find_solution2(word_index=wi_loaded, cross_words_index=cross_words_index,
                                 orig_grid=grid)
            print(sol)