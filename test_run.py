import time
import random
# import unittest

from karnobh.crosswordist.affine_2d import (FlatMatrix, point, translate, rotate, scale, identity,
                                            WrongMatrixDimension)
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, WordDirection)
from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)
from karnobh.crosswordist.solution_finder import find_solution, find_solution2, _as_flat_matrix

import sys


def test_run():
    # random.seed(1)
    with open('/tmp/words_tests/index.json') as f:
        wi_loaded = WordsIndex(file=f)
    found_times = 0
    for num in range(100):
        # if num % 10 == 0:
            # logger.info("Generated numbers = %s", num)
        print("test_finding_solution_with_generating::Generated_nums = ", num)
        grid_size = 15
        symmetry = random.choice(["X", "NO"])
        grid = create_random_grid(grid_size, symmetry="X")
        print("grid: \n", grid.pretty_log({0: "□", 1: "■"}))
        words_layout = get_all_checked_words_layout(grid)
        cross_words_index = create_cross_words_index(words_layout, grid)
        print(cross_words_index)
        t0 = time.time()
        sol = find_solution2(word_index=wi_loaded, cross_words_index=cross_words_index,
                             orig_grid=grid)
        sol_results = {
            0: "Found",
            1: "Does not exist",
            2: "Timed Out"
        }
        if sol == 0:
            found_times += 1
        print(f"Solution: {sol_results[sol]} ==> time: {time.time() - t0} seconds ==>"
              f"found ratio: {found_times / (num + 1)}")
        print(_as_flat_matrix(cross_words_index, grid).pretty_log({0: "■", "": "□"}))


if __name__ == '__main__':
    test_run()
