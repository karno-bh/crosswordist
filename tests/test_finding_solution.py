import time
import random
import unittest
import importlib.resources as pkg_res

from karnobh.crosswordist.affine_2d import FlatMatrix
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, CrossWordsIndex)
from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.word_index_native import WordIndexNative
from karnobh.crosswordist.solution_finder import find_solution, FinderResult


class TestFiningSolution(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assets_package = 'tests.assets'
        self.corpus_file = 'random_filtered_words.txt'
        self.index_file = 'random_filtered_words_idx.json'

    def test_cross_word_index_creation2(self):
        grid_data = [0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     1, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 1,
                     0, 0, 0, 1, 1, 1, 1]
        size = 7
        grid = FlatMatrix(size, size, new_state=grid_data)
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            wi_loaded = WordsIndex(file=f)
        cross_words_index = CrossWordsIndex(grid=grid)
        random.seed(1)
        sol = find_solution(word_index=wi_loaded,
                            cross_words_index=cross_words_index,
                            timeout_after_seconds=10)
        actual_gird = cross_words_index.letters_matrix.pretty_log({0: "#", "": " "})
        expected_grid = """\
        B R N # R T G
        A I A # E W O
        O P T # M I N
        # P I S A C A
        C L O C K E D
        T E N S E R #
        M R S # # # #
        """
        expected_grid = "\n".join(l.strip() for l in expected_grid.split("\n"))
        self.assertEqual(FinderResult.FOUND, sol)
        self.assertEqual(expected_grid, actual_gird)

    def test_cross_word_index_equality(self):
        grid_data = [0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     1, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 1,
                     0, 0, 0, 1, 1, 1, 1]
        size = 7
        grid = FlatMatrix(size, size, new_state=grid_data)
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            wi_loaded = WordsIndex(file=f)
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            wi_loaded_native = WordIndexNative(file=f)
        cross_words_index = CrossWordsIndex(grid=grid)
        cross_words_index_native = CrossWordsIndex(grid=grid)
        random.seed(1)
        sol = find_solution(word_index=wi_loaded,
                            cross_words_index=cross_words_index,
                            timeout_after_seconds=10)
        grid = cross_words_index.letters_matrix.pretty_log({0: "#", "": " "})
        random.seed(1)
        sol_native = find_solution(word_index=wi_loaded_native,
                                   cross_words_index=cross_words_index_native,
                                   timeout_after_seconds=10)
        grid_native = cross_words_index_native.letters_matrix.pretty_log({0: "#", "": " "})
        self.assertEqual(sol, sol_native)
        self.assertEqual(grid, grid_native)

    def dont_test_finding_solution_with_generating(self):
        random.seed(1)
        # with open('/tmp/words_tests/index.json') as f:
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            wi_loaded = WordIndexNative(file=f)
        found_times = 0
        for num in range(100):
            # if num % 10 == 0:
                # logger.info("Generated numbers = %s", num)
            print("test_finding_solution_with_generating::Generated_nums = ", num)
            grid_size = 7
            symmetry = random.choice(["X", "NO"])
            grid = create_random_grid(grid_size, symmetry="NO")
            print("grid: \n", grid.pretty_log({0: "□", 1: "■"}))
            words_layout = get_all_checked_words_layout(grid)
            # cross_words_index = create_cross_words_index(words_layout, grid)
            # print(cross_words_index)
            cross_words_index = CrossWordsIndex(grid)
            t0 = time.time()
            sol = find_solution(word_index=wi_loaded,
                                cross_words_index=cross_words_index,
                                timeout_after_seconds=10)
            sol_results = {
                FinderResult.FOUND: "Found",
                FinderResult.NO_SOLUTION: "Does not exist",
                FinderResult.TIMED_OUT: "Timed Out"
            }
            if sol == FinderResult.FOUND:
                found_times += 1
            print(f"Solution: {sol_results[sol]} ==> time: {time.time() - t0} seconds ==>"
                  f"found ratio: {found_times / (num + 1)}")
            print(cross_words_index.letters_matrix.pretty_log({0: "■", "": "□"}))
