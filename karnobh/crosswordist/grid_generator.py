"""
The module is responsible for generating crossword's grid in different forms. That is, it contains
generators for the grid itself as a matrix. It contains auxiliary functions for taking the matrix
and representing it as a layout of all words in that matrix (i.e., arrays of vertical words and
horizontal words, where each position is the "number" of the word). Finally, it contains a class
that represents a given matrix (or grid) as an index of all words crossing each other (i.e., the
graph of all crossing words; the term index is used here since from the outside one can get access
to some word by its number and direction)
"""
import itertools
import random
import time
from dataclasses import dataclass
from enum import Enum
import weakref
from typing import Any
from karnobh.crosswordist.affine_2d import FlatMatrix, translate, ROT_INT_90, point


class WordDirection(Enum):
    """
    Enum that represents the direction of the word
    """
    HORIZONTAL = 0
    VERTICAL = 1


class WordLayoutError(Exception):
    pass


@dataclass(slots=True, init=False, repr=False)
class WordLayout:
    """
    Representing a word as a Word Layout. That is, full representation of the cells in the grid for
    some word. It does not have to be a fully set word, it may be a partially set word. In addition,
    the instance of a class also has references to all other words that the current word intersect
    (thus forming a graph). A graph in such representation will form circle references. Thus, the
    references to other nodes (word layouts) in a graph are weak references.
    """
    word_num: int
    direction: WordDirection
    x_init: int
    y_init: int
    word_len: int
    word_letters: list[str]
    word_intersects: list[tuple]
    _filled_letters: int
    _mapping: dict[int, str] | None
    __weakref__: Any

    def __init__(self, word_num, direction, x_init, y_init, word_len):
        self.word_num = word_num
        self.direction = direction
        self.x_init = x_init
        self.y_init = y_init
        self.word_len = word_len
        self.word_letters = [""] * self.word_len
        self.word_intersects = [()] * self.word_len
        self._filled_letters = -1
        self._mapping = None

    def __repr__(self):
        """
        The default representation of the "dataclass" is not suitable because it gets into infinite
        recursion.
        :return: representation of a word layout
        """
        word_intersects_repr = []
        for word in self.word_intersects:
            if word:
                intersected_word: WordLayout = word[0]
                intersected_pos: int = word[1]
                dir_letter = 'H' if intersected_word.direction == WordDirection.HORIZONTAL else 'V'
                repr_state = (intersected_word.word_num, dir_letter, intersected_pos)
            else:
                repr_state = ()
            word_intersects_repr.append(repr_state)

        return (f"WordLayout({self.word_num}, "
                f"{'H' if self.direction == WordDirection.HORIZONTAL else 'V'}, {self.x_init}, "
                f"{self.y_init}, {self.word_len}, {self.word_letters}, {word_intersects_repr})")

    def _set_letter(self, letter: str, index: int, propagate=True):
        """
        This method sets (or unsets) the letter in some position of a word. As well, it recursively
        propagates the set letter to the crossing words. The propagation should happen only once
        since the for some specific letter at some position there is only two adjacent words.
        :param letter: The character of a letter to be set
        :param index: The position of the letter
        :param propagate: whether to propagate the letter setting or not. External calls should not
               set this parameter. It is used for recursive calls.
        :return: None - it internally mutates the state of the current word cells and adjacent.
        """
        self._filled_letters = -1
        self._mapping = None
        if letter and self.word_letters[index] and letter != self.word_letters[index]:
            raise WordLayoutError(f"There is already letter '{self.word_letters[index]}' "
                                  f"at index {index}. "
                                  f"Trying to set letter '{letter}'. {self}")
        self.word_letters[index] = letter
        if propagate:
            crossing_word_layout, crossing_word_index = self.word_intersects[index]
            crossing_word_layout._set_letter(letter, crossing_word_index, propagate=False)

    def set_word(self, word):
        """
        Set word into current layout. The word length should be of the same length
        :param word: word to set
        :return: None - mutates current word and crossing adjacent words
        """
        for i, letter in enumerate(word):
            self._set_letter(letter, i)

    @property
    def filled_letters(self) -> int:
        """
        :return: Number of non-empty letters in current word. The value is cached until a letter of
                 the word changed.
        """
        if self._filled_letters == -1:
            self._filled_letters = sum(1 for letter in self.word_letters if letter != '')
        return self._filled_letters

    @property
    def mapping(self) -> dict[int, str]:
        """
        :return: Position to letter (i.e., "sparse array") mapping of the word
        """
        if self._mapping is None:
            self._mapping = {i: l for i, l in enumerate(self.word_letters) if l}
        return self._mapping

    @property
    def full(self) -> bool:
        """
        :return: Boolean value whether all letters of the word are set
        """
        return self.filled_letters == self.word_len


class GridGenerationError(Exception):
    pass


def create_random_grid(size, black_ratio=1 / 6, all_checked=True, symmetry='X',
                       min_word_size=3, timeout_seconds=3):
    inc_vectors = [-1 + 0j, 1 + 0j, 0 - 1j, 0 + 1j]
    transform_mt_90: FlatMatrix = translate(size - 1, 0) * ROT_INT_90
    pane = FlatMatrix(size, size)
    max_blacks = int(size * size * black_ratio)
    start_time = time.time()
    blacks_num = 0
    iterations = 0
    while blacks_num <= max_blacks:
        iterations += 1
        if iterations > size ** 3:
            delta_time = time.time() - start_time
            if delta_time >= timeout_seconds:
                raise GridGenerationError(f"Grid generation timed "
                                          f"out after {timeout_seconds} seconds")
            pane = FlatMatrix(size, size)
            blacks_num = 0
            iterations = 0
        regen_points = False
        if symmetry == 'X':
            points = ([pt := point(*[random.randint(0, size - 1) for _ in range(2)])] +
                      [pt := transform_mt_90 * pt for _ in range(3)])
        elif symmetry == 'D':
            points = ([pt := point(*[random.randint(0, size - 1) for _ in range(2)])] +
                      [pt := transform_mt_90 * pt for _ in range(2)])
            del points[1]
        elif symmetry == 'NO':
            points = [point(*[random.randint(0, size - 1) for _ in range(2)])]
        else:
            raise GridGenerationError(f"Symmetry {symmetry} is not supported")
        for x, y, *_ in points:
            if pane.get(x, y) != 0:
                regen_points = True
                break
        if regen_points:
            continue
        for x, y, *_ in points:
            pane.set(x, y, 1, clone=False)
        blacks_num += len(points)
        for x, y, *_ in points:
            if all_checked:
                current = complex(x, y)
                vectors = [current + iv for iv in inc_vectors]
                for vec, inc_vec in zip(vectors, inc_vectors):
                    d = 0
                    while (d < min_word_size and not pane.out_of_range(vec.real, vec.imag)
                           and pane.get(int(vec.real), int(vec.imag)) == 0):
                        vec += inc_vec
                        d += 1
                    if d > 0 and d != min_word_size:
                        regen_points = True
                        break
            else:
                raise GridGenerationError("all_checked=False not supported")
        if regen_points:
            for x, y, *_ in points:
                pane.set(x, y, 0, clone=False)
            blacks_num -= len(points)
    return pane


def get_all_checked_words_layout(
        grid: FlatMatrix) -> list[list[tuple[WordDirection, int, int, int]]]:
    width, height = grid.size
    layout = []
    for j in range(height):
        for i in range(width):
            word_horiz_len, word_vert_len = 0, 0
            if grid.out_of_range(i - 1, j) or grid.get(i - 1, j) == 1:
                word_i = i
                while not grid.out_of_range(word_i, j) and grid.get(word_i, j) != 1:
                    word_i += 1
                word_horiz_len = word_i - i
                if word_horiz_len > 0:
                    layout.append([(WordDirection.HORIZONTAL, i, j, word_horiz_len)])
            if grid.out_of_range(i, j - 1) or grid.get(i, j - 1) == 1:
                word_j = j
                while not grid.out_of_range(i, word_j) and grid.get(i, word_j) != 1:
                    word_j += 1
                word_vert_len = word_j - j
                if word_vert_len > 0:
                    word_vert_data = (WordDirection.VERTICAL, i, j, word_vert_len)
                    if word_horiz_len > 0:
                        layout[-1].append(word_vert_data)
                    else:
                        layout.append([word_vert_data])

    return layout


def create_cross_words_index(words_layout: list[list[tuple[WordDirection, int, int, int]]],
                             grid: FlatMatrix) -> tuple[list[WordLayout], list[WordLayout]]:
    width, height = grid.size
    vertical_index: list[list[WordLayout]] = [[] for _ in range(width)]
    horizontal_index: list[list[WordLayout]] = [[] for _ in range(height)]
    vertical_words: list[WordLayout] = []
    horizontal_words: list[WordLayout] = []
    for word_num, word_layout in enumerate(words_layout):
        for pos_word_layout in word_layout:
            word_dir, x_init, y_init, word_len = pos_word_layout
            pos_word_layout_data = WordLayout(
                word_num=word_num,
                direction=word_dir,
                x_init=x_init,
                y_init=y_init,
                word_len=word_len
            )
            if word_dir == WordDirection.VERTICAL:
                vertical_words.append(pos_word_layout_data)
                vertical_index[x_init].append(pos_word_layout_data)
            else:
                horizontal_words.append(pos_word_layout_data)
                horizontal_index[y_init].append(pos_word_layout_data)

    for vertical_word in vertical_words:
        y_init = vertical_word.y_init
        x_init = vertical_word.x_init
        word_len = vertical_word.word_len
        for y_coord in range(y_init, y_init + word_len):
            horizontal_words_in_y = horizontal_index[y_coord]
            for horizontal_word_in_y in horizontal_words_in_y:
                hw_i_x = horizontal_word_in_y.x_init
                hw_len = horizontal_word_in_y.word_len
                if hw_i_x <= x_init < hw_i_x + hw_len:
                    vertical_word_intersect_pos = y_coord - y_init
                    horizontal_word_intersect_pos = x_init - hw_i_x
                    vertical_word.word_intersects[vertical_word_intersect_pos] = (
                        weakref.proxy(horizontal_word_in_y),
                        horizontal_word_intersect_pos
                    )
                    horizontal_word_in_y.word_intersects[horizontal_word_intersect_pos] = (
                        weakref.proxy(vertical_word),
                        vertical_word_intersect_pos
                    )
                    break

    return horizontal_words, vertical_words


class CrossWordsIndexError(Exception):
    pass


class CrossWordsIndex:

    def __init__(self, grid: FlatMatrix):
        super().__init__()
        self.grid = grid
        all_checked_words_layout = self._get_all_checked_words_layout(grid)
        self.horizontal_words, self.vertical_words = self._create_cross_words_index(
            all_checked_words_layout,
            grid
        )

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, grid):
        if not isinstance(grid, FlatMatrix):
            raise CrossWordsIndexError(f"Grid should be of type FlatMatrix, got {type(grid)}")
        self._grid = grid

    @property
    def horizontal_words(self):
        return self._horizontal_words

    @horizontal_words.setter
    def horizontal_words(self, horizontal_words):
        if not isinstance(horizontal_words, list):
            raise CrossWordsIndexError(f"Horizontal words should be a list, "
                                       f"got {type(horizontal_words)}")
        self._horizontal_words = horizontal_words

    @property
    def vertical_words(self):
        return self._vertical_words

    @vertical_words.setter
    def vertical_words(self, vertical_words):
        if not isinstance(vertical_words, list):
            raise CrossWordsIndexError(f"Horizontal words should be a list, "
                                       f"got {type(vertical_words)}")
        self._vertical_words = vertical_words

    def _get_all_checked_words_layout(
            self,
            grid: FlatMatrix) -> list[list[tuple[WordDirection, int, int, int]]]:
        return get_all_checked_words_layout(grid)

    def _create_cross_words_index(self,
                                  words_layout: list[list[tuple[WordDirection, int, int, int]]],
                                  grid: FlatMatrix) -> tuple[list[WordLayout], list[WordLayout]]:
        return create_cross_words_index(words_layout, grid)

    @property
    def letters_matrix(self) -> FlatMatrix:
        width, height = self.grid.size
        res = FlatMatrix(width=width, height=height)
        for word_layout in self.all:
            if word_layout.direction == WordDirection.VERTICAL:
                for y_coord in range(word_layout.y_init, word_layout.y_init + word_layout.word_len):
                    res.set(word_layout.x_init, y_coord,
                            val=word_layout.word_letters[y_coord - word_layout.y_init],
                            clone=False)
            elif word_layout.direction == WordDirection.HORIZONTAL:
                for x in range(word_layout.x_init, word_layout.x_init + word_layout.word_len):
                    res.set(x, word_layout.y_init,
                            val=word_layout.word_letters[x - word_layout.x_init],
                            clone=False)
        return res

    @property
    def all(self):
        return itertools.chain(self.horizontal_words, self.vertical_words)
