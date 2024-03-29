import random
import time
import unittest
import math

import karnobh.crosswordist.log_config as log_config
log_config.set_logger()
import logging
from karnobh.crosswordist.affine_2d import (FlatMatrix, point, translate, rotate, scale, identity,
                                            WrongMatrixDimension)
from karnobh.crosswordist.grid_generator import (create_random_grid, get_all_checked_words_layout,
                                                 create_cross_words_index, WordDirection,
                                                 GridGenerationError)

logger = logging.getLogger(__name__)

class TestFlatMatrix(unittest.TestCase):

    def test_flat_matrix_creation_default(self):
        size = 5
        expected_default = 0
        matrix = FlatMatrix(size, size)
        res = []
        for i in range(size):
            for j in range(size):
                val_at_xy = matrix.get(i, j)
                if val_at_xy != expected_default:
                    res.append(val_at_xy)
        expected = []
        self.assertEqual(expected, res)

    def test_flat_matrix_creation_default_val(self):
        size = 5
        expected_default = 42
        matrix = FlatMatrix(size, size, initial_val=expected_default)
        res = []
        for i in range(size):
            for j in range(size):
                val_at_xy = matrix.get(i, j)
                if val_at_xy != expected_default:
                    res.append(val_at_xy)
        expected = []
        self.assertEqual(expected, res)

    def test_flat_matrix_creation_from_data(self):
        expected = list(range(9))
        matrix = FlatMatrix(3, 3, new_state=expected)
        res = []
        for y in range(3):
            for x in range(3):
                res.append(matrix.get(x, y))
        self.assertEqual(expected, res)

    def test_flat_matrix_set_without_clone(self):
        matrix = FlatMatrix(3, 3)
        val = 0
        for y in range(3):
            for x in range(3):
                matrix.set(x, y, val=val, clone=False)
                val += 1
        res = []
        for y in range(3):
            for x in range(3):
                res.append(matrix.get(x, y))
        expected = list(range(9))
        self.assertEqual(expected, res)

    def test_flat_matrix_set_with_clone(self):
        matrix = FlatMatrix(3, 3)
        second_matrix = matrix.set(0, 0, 42)
        self.assertEqual(0, matrix.get(0, 0))
        self.assertEqual(42, second_matrix.get(0, 0))

    def test_out_of_range(self):
        matrix = FlatMatrix(3, 3)
        for x in range(3):
            for y in range(3):
                self.assertEqual(False, matrix.out_of_range(x, y))
        self.assertEqual(True, matrix.out_of_range(-1, 0))
        self.assertEqual(True, matrix.out_of_range(0, -1))
        self.assertEqual(True, matrix.out_of_range(3, 0))
        self.assertEqual(True, matrix.out_of_range(0, 3))

    def test_str(self):
        matrix = FlatMatrix(3,3, new_state=list(range(9)))
        expected = "0 1 2\n3 4 5\n6 7 8\n"
        self.assertEqual(expected, str(matrix))

    def test_pretty_print(self):
        matrix = FlatMatrix(3,3)
        matrix.set(1,1, 1, clone=False)
        pretty_str = matrix.pretty_log(replace={0: '-', 1: 'X'})
        expected = "- - -\n- X -\n- - -\n"
        self.assertEqual(expected, pretty_str)

    def test_matrix_mul_vec(self):
        matrix = FlatMatrix(3,3, new_state=list(range(1, 10)))
        res = matrix * [1, 2, 3]
        expected = [14, 32, 50]
        self.assertEqual(expected, res)

    def test_matrix_mul_matrix(self):
        matrix = translate(4, 4, int) * scale(1/2, 1/2, float) * rotate(math.pi, int) * scale(2, 2, int) * rotate(math.pi, int) * translate(-4, -4)
        expected = identity(float)
        self.assertEqual(expected.data, matrix.data)
        for i in range(1, 20):
            pt = point(random.randint(0, 100), random.randint(0, 100))
            self.assertEqual(expected * pt, matrix * pt)

    def test_non_int_matrix_generators(self):
        mat1 = (translate(0.0, -10.0, elem_type=float) * translate(-10.0, 0.0, elem_type=float) *
                translate(0.0, 10.0, elem_type=float) * translate(10.0, 0.0, elem_type=float))
        expected = identity(float)
        self.assertEqual(expected, mat1)

    def test_exceptional_exists(self):
        m1 = identity(int)
        m2 = FlatMatrix(4, 4, new_state=[
            1, 0,
            0, 1,
        ])
        self.assertRaises(WrongMatrixDimension, lambda: m1 * m2)
        v1 = [1, 0, 1]
        self.assertRaises(WrongMatrixDimension, lambda: m2 * v1)
        self.assertRaises(TypeError, lambda: m1 * (1, 1, 1))


class TestGridGenerating(unittest.TestCase):

    def test_all_checked_generated_words(self):
        for num in range(1000):
            if num % 100 == 0:
                logger.info("Generated numbers = %s", num)
                # print("test_all_checked_generated_words::Generated_nums = ", num)
            grid_size = 15
            symmetry = random.choice(["X", "NO"])
            grid = create_random_grid(grid_size, symmetry=symmetry)
            # print(grid)
            # print(grid.data)
            # data = [1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1]
            # grid = FlatMatrix(grid_size, grid_size, new_state=data)
            words_layout = get_all_checked_words_layout(grid)
            # print(words_layout)
            # print(len(words_layout))
            test_matrix = FlatMatrix(grid_size, grid_size, initial_val=2)
            min_word = grid_size + 1
            for word_layout in words_layout:
                for pos_word_layout in word_layout:
                    word_dir, x_init, y_init, word_len = pos_word_layout
                    min_word = min(min_word, word_len)
                    if word_dir == WordDirection.HORIZONTAL:
                        if not test_matrix.out_of_range(x_init - 1, y_init):
                            test_matrix.set(x_init - 1, y_init, 1, clone=False)
                        for x in range(x_init, x_init + word_len):
                            test_matrix.set(x, y_init, 0, clone=False)
                    elif word_dir == WordDirection.VERTICAL:
                        if not test_matrix.out_of_range(x_init, y_init - 1):
                            test_matrix.set(x_init, y_init - 1, 1, clone=False)
                        for y in range(y_init, y_init + word_len):
                            test_matrix.set(x_init, y, 0, clone=False)
            for i in range(grid_size):
                for j in range(grid_size):
                    if (test_matrix.get(i, j) == 2 and
                        (test_matrix.out_of_range(i + 1, j) or test_matrix.get(i + 1, j) in (1, 2)) and
                        (test_matrix.out_of_range(i, j + 1) or test_matrix.get(i, j + 1) in (1, 2))):
                        test_matrix.set(i, j, 1, clone=False)
            self.assertEqual(grid.data, test_matrix.data)
            self.assertGreater(min_word, 2)

    def test_grid_generation_time_out(self):
        with self.assertRaises(GridGenerationError) as cm:
            grid_size = 15
            symmetry = "X"
            random.seed(1)
            grid = create_random_grid(
                grid_size,
                symmetry=symmetry,
                black_ratio=1/2,
                timeout_seconds=2
            )
            print(grid)
        expected_exception_str = "Grid generation timed out after 2 seconds"
        self.assertEqual(
            expected_exception_str,
            str(cm.exception)
        )

    def test_grid_generation_diagonal_symmetry(self):
        grid_size = 7
        symmetry = "D"
        random.seed(1)
        grid = create_random_grid(
            grid_size,
            symmetry=symmetry,
        )
        expected = [
            1, 0, 0, 0, 0, 0, 1,
            0, 0, 0, 0, 0, 0, 1,
            0, 0, 0, 0, 0, 0, 1,
            0, 0, 0, 1, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 1,
        ]
        self.assertEqual(expected, grid.data)

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
        cross_words_index = create_cross_words_index(words_layout, grid)
        print(cross_words_index)

    def dont_test_memory_of_index(self):
        t0 = time.time()
        for num in range(1000):
            if num % 100 == 0:
                logger.info("Generated numbers = %s", num)
                # print("test_all_checked_generated_words::Generated_nums = ", num)
            grid_size = 15
            symmetry = random.choice(["X", "NO"])
            grid = create_random_grid(grid_size, symmetry=symmetry)
            words_layout = get_all_checked_words_layout(grid)
            cross_words_index = create_cross_words_index(words_layout, grid)
            # print(cross_words_index)
        print("total time: ", time.time() - t0)