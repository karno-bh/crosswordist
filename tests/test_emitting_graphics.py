import unittest

import importlib.resources as pkg_res
import random
from io import StringIO

from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.affine_2d import FlatMatrix
from karnobh.crosswordist.grid_generator import CrossWordsIndex
from karnobh.crosswordist.grid_emitter import emit_graphics_objects, draw_crossword
from karnobh.crosswordist.graphics import SvgGraphicsEmitter, EmitterContext
from karnobh.crosswordist.solution_finder import find_solution


class EmittingGraphicsTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assets_package = 'tests.assets'
        self.corpus_file = 'random_filtered_words.txt'
        self.index_file = 'random_filtered_words_idx.json'

    def test_emitting(self):
        grid_data = [0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     0, 0, 0, 1, 0, 0, 0,
                     1, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 1,
                     0, 0, 0, 1, 1, 1, 1]
        size = 7
        grid = FlatMatrix(size, size, new_state=grid_data)
        cross_words_index = CrossWordsIndex(grid=grid)

        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            wi_loaded = WordsIndex(file=f)
        random.seed(1)
        sol = find_solution(word_index=wi_loaded,
                            cross_words_index=cross_words_index,
                            timeout_after_seconds=10)
        expected = """\
        <rect x='0' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='0' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='0' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='0' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='0' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='0' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='0' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='85' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='170' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='255' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='255' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='255' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='255' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='255' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='255' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='255' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='340' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='340' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='340' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='340' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='340' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='340' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='340' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='425' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='425' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='425' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='425' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='425' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='425' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='425' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='510' y='0' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='510' y='85' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='510' y='170' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='510' y='255' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='510' y='340' width='85' height='85' stroke='black' stroke-width='2' fill='white' />
        <rect x='510' y='425' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <rect x='510' y='510' width='85' height='85' stroke='black' stroke-width='2' fill='black' />
        <text x='6' y='352' text-anchor='start' font-size='12'>13</text>
        <text x='346' y='97' text-anchor='start' font-size='12'>8</text>
        <text x='346' y='12' text-anchor='start' font-size='12'>4</text>
        <text x='91' y='12' text-anchor='start' font-size='12'>2</text>
        <text x='6' y='182' text-anchor='start' font-size='12'>9</text>
        <text x='6' y='12' text-anchor='start' font-size='12'>1</text>
        <text x='431' y='12' text-anchor='start' font-size='12'>5</text>
        <text x='91' y='267' text-anchor='start' font-size='12'>11</text>
        <text x='6' y='437' text-anchor='start' font-size='12'>14</text>
        <text x='516' y='12' text-anchor='start' font-size='12'>6</text>
        <text x='6' y='522' text-anchor='start' font-size='12'>15</text>
        <text x='6' y='97' text-anchor='start' font-size='12'>7</text>
        <text x='346' y='182' text-anchor='start' font-size='12'>10</text>
        <text x='176' y='12' text-anchor='start' font-size='12'>3</text>
        <text x='261' y='267' text-anchor='start' font-size='12'>12</text>
        <text x='42' y='77' text-anchor='middle' font-size='72'>B</text>
        <text x='42' y='162' text-anchor='middle' font-size='72'>A</text>
        <text x='42' y='247' text-anchor='middle' font-size='72'>O</text>
        <text x='42' y='417' text-anchor='middle' font-size='72'>C</text>
        <text x='42' y='502' text-anchor='middle' font-size='72'>T</text>
        <text x='42' y='587' text-anchor='middle' font-size='72'>M</text>
        <text x='127' y='77' text-anchor='middle' font-size='72'>R</text>
        <text x='127' y='162' text-anchor='middle' font-size='72'>I</text>
        <text x='127' y='247' text-anchor='middle' font-size='72'>P</text>
        <text x='127' y='332' text-anchor='middle' font-size='72'>P</text>
        <text x='127' y='417' text-anchor='middle' font-size='72'>L</text>
        <text x='127' y='502' text-anchor='middle' font-size='72'>E</text>
        <text x='127' y='587' text-anchor='middle' font-size='72'>R</text>
        <text x='212' y='77' text-anchor='middle' font-size='72'>N</text>
        <text x='212' y='162' text-anchor='middle' font-size='72'>A</text>
        <text x='212' y='247' text-anchor='middle' font-size='72'>T</text>
        <text x='212' y='332' text-anchor='middle' font-size='72'>I</text>
        <text x='212' y='417' text-anchor='middle' font-size='72'>O</text>
        <text x='212' y='502' text-anchor='middle' font-size='72'>N</text>
        <text x='212' y='587' text-anchor='middle' font-size='72'>S</text>
        <text x='297' y='332' text-anchor='middle' font-size='72'>S</text>
        <text x='297' y='417' text-anchor='middle' font-size='72'>C</text>
        <text x='297' y='502' text-anchor='middle' font-size='72'>S</text>
        <text x='382' y='77' text-anchor='middle' font-size='72'>R</text>
        <text x='382' y='162' text-anchor='middle' font-size='72'>E</text>
        <text x='382' y='247' text-anchor='middle' font-size='72'>M</text>
        <text x='382' y='332' text-anchor='middle' font-size='72'>A</text>
        <text x='382' y='417' text-anchor='middle' font-size='72'>K</text>
        <text x='382' y='502' text-anchor='middle' font-size='72'>E</text>
        <text x='467' y='77' text-anchor='middle' font-size='72'>T</text>
        <text x='467' y='162' text-anchor='middle' font-size='72'>W</text>
        <text x='467' y='247' text-anchor='middle' font-size='72'>I</text>
        <text x='467' y='332' text-anchor='middle' font-size='72'>C</text>
        <text x='467' y='417' text-anchor='middle' font-size='72'>E</text>
        <text x='467' y='502' text-anchor='middle' font-size='72'>R</text>
        <text x='552' y='77' text-anchor='middle' font-size='72'>G</text>
        <text x='552' y='162' text-anchor='middle' font-size='72'>O</text>
        <text x='552' y='247' text-anchor='middle' font-size='72'>N</text>
        <text x='552' y='332' text-anchor='middle' font-size='72'>A</text>
        <text x='552' y='417' text-anchor='middle' font-size='72'>D</text>"""
        expected_lines = [line.strip() for line in expected.split("\n")]
        with StringIO() as f:
            graphics_emitter = SvgGraphicsEmitter(f)
            draw_crossword(cross_words_index, graphics_emitter)
            f.seek(0)
            actual_lines = [line.strip() for line in f]

        self.assertEqual(expected_lines, actual_lines)
