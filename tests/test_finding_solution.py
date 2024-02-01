import time
import random
import unittest

from karnobh.crosswordist.affine_2d import FlatMatrix
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, CrossWordsIndex)
from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.solution_finder import find_solution, FinderResult

# import sys

# Set the stack size to 30000
# sys.setrecursionlimit(30000)


class TestFiningSolution(unittest.TestCase):

    def test_cross_word_index_creation2(self):
        random.seed(1)
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
        # cross_words_index = create_cross_words_index(words_layout, grid)
        # print(cross_words_index)
        with open('/tmp/words_tests/index.json') as f:
            wi_loaded = WordsIndex(file=f)
        cross_words_index = CrossWordsIndex(grid=grid)
        print("grid: \n", grid.pretty_log({0: "_", 1: "*"}))
        sol = find_solution(word_index=wi_loaded,
                            cross_words_index=cross_words_index,
                            timeout_after_seconds=30)
        print(sol)
        sol_results = {
            FinderResult.FOUND: "Found",
            FinderResult.NO_SOLUTION: "Does not exist",
            FinderResult.TIMED_OUT: "Timed Out"
        }
        print(f"Solution: {sol_results[sol]} ")
        print(cross_words_index.letters_matrix.pretty_log({0: "■", "": "□"}))


    def dont_test_finding_solution_with_generating(self):
        # random.seed(1)
        with open('/tmp/words_tests/index.json') as f:
            wi_loaded = WordsIndex(file=f)
        found_times = 0
        for num in range(100):
            if num % 10 == 0:
                # logger.info("Generated numbers = %s", num)
                print("test_finding_solution_with_generating::Generated_nums = ", num)
            grid_size = 15
            symmetry = random.choice(["X", "NO"])
            grid = create_random_grid(grid_size, symmetry="X")
            print("grid: \n", grid.pretty_log({0: "□", 1: "■"}))
            words_layout = get_all_checked_words_layout(grid)
            # cross_words_index = create_cross_words_index(words_layout, grid)
            # print(cross_words_index)
            cross_words_index = CrossWordsIndex(grid)
            t0 = time.time()
            sol = find_solution(word_index=wi_loaded,
                                cross_words_index=cross_words_index,
                                timeout_after_seconds=30)
            sol_results = {
                FinderResult.FOUND: "Found",
                FinderResult.NO_SOLUTION: "Does not exist",
                FinderResult.TIMED_OUT: "Timed Out"
            }
            if sol == 0:
                found_times += 1
            print(f"Solution: {sol_results[sol]} ==> time: {time.time() - t0} seconds ==>"
                  f"found ratio: {found_times / (num + 1)}")
            print(cross_words_index.letters_matrix.pretty_log({0: "■", "": "□"}))
