import time
import random
# import unittest

from karnobh.crosswordist.affine_2d import (FlatMatrix, point, translate, rotate, scale, identity,
                                            WrongMatrixDimension)
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, WordDirection, CrossWordsIndex)
from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)
from karnobh.crosswordist.solution_finder import find_solution, FinderResult

import sys


def test_run():
    # random.seed(1)
    native_mode = True
    with open('/tmp/words_tests/index.json') as f:
        if native_mode:
            from karnobh.crosswordist.word_index_native import WordIndexNative
            wi_loaded = WordIndexNative(file=f)
        else:
            wi_loaded = WordsIndex(file=f)
    found_times = 0
    total_found_secs = 0
    for num in range(100):
        # if num % 10 == 0:
            # logger.info("Generated numbers = %s", num)
        print("test_finding_solution_with_generating::Generated_nums = ", num)
        grid_size = 11
        symmetry = random.choice(["X", "NO"])
        grid = create_random_grid(grid_size, symmetry="X")
        print("grid: \n", grid.pretty_log({0: "□", 1: "■"}))
        # words_layout = get_all_checked_words_layout(grid)
        # cross_words_index = create_cross_words_index(words_layout, grid)
        # print(cross_words_index)
        cross_words_index = CrossWordsIndex(grid=grid)
        t0 = time.time()
        sol = find_solution(word_index=wi_loaded,
                            cross_words_index=cross_words_index,
                            timeout_after_seconds=5)
        sol_results = {
            FinderResult.FOUND: "Found",
            FinderResult.NO_SOLUTION: "Does not exist",
            FinderResult.TIMED_OUT: "Timed Out"
        }
        solution_secs = time.time() - t0
        if sol == FinderResult.FOUND:
            found_times += 1
            total_found_secs += solution_secs
        print(f"Solution: {sol_results[sol]} ==> time: {solution_secs} seconds ==>"
              f"found ratio: {found_times / (num + 1)}")
        print(cross_words_index.letters_matrix.pretty_log({0: "■", "": "□"}))
    if found_times > 0:
        print("Average time per soulution: ", total_found_secs / found_times)


if __name__ == '__main__':
    test_run()
