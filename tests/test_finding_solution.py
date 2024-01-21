import unittest

from karnobh.crosswordist.affine_2d import (FlatMatrix, point, translate, rotate, scale, identity,
                                            WrongMatrixDimension)
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, WordDirection)
from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)
from karnobh.crosswordist.solution_finder import find_solution


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
