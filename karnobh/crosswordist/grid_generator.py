import itertools
import random
from dataclasses import dataclass
import weakref
from typing import Any
from karnobh.crosswordist.affine_2d import FlatMatrix, translate, ROT_INT_90, point


class WordDirection:
    HORIZONTAL = 0
    VERTICAL = 1


@dataclass(slots=True, init=False, repr=False)
class WordLayout:
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
        self._filled_letters = -1
        self._mapping = None
        if letter and self.word_letters[index] and letter != self.word_letters[index]:
            raise Exception(f"There is already letter '{self.word_letters[index]}' "
                            f"at index {index}. Trying to set letter '{letter}'. {self}")
        self.word_letters[index] = letter
        if propagate:
            crossing_word_layout, crossing_word_index = self.word_intersects[index]
            crossing_word_layout._set_letter(letter, crossing_word_index, propagate=False)

    def set_word(self, word):
        for i, l in enumerate(word):
            self._set_letter(l, i)

    @property
    def filled_letters(self):
        if self._filled_letters == -1:
            self._filled_letters = sum(1 for letter in self.word_letters if letter != '')
        return self._filled_letters

    @property
    def mapping(self):
        if self._mapping is None:
            self._mapping = {i: l for i, l in enumerate(self.word_letters) if l}
        return self._mapping

    @property
    def full(self):
        return self.filled_letters == self.word_len


def create_random_grid(size, black_ratio=1 / 6, all_checked=True, symmetry='X',
                       min_word_size=3):
    inc_vectors = [-1 + 0j, 1 + 0j, 0 - 1j, 0 + 1j]
    transform_mt_90: FlatMatrix = translate(size - 1, 0) * ROT_INT_90
    pane = FlatMatrix(size, size)
    max_blacks = int(size * size * black_ratio)
    blacks_num = 0
    iterations = 0
    while blacks_num <= max_blacks:
        iterations += 1
        if iterations > size ** 3:
            pane = FlatMatrix(size, size)
            blacks_num = 0
            iterations = 0
        regen_points = False
        if symmetry == 'X':
            points = ([p := point(*[random.randint(0, size - 1) for _ in range(2)])] +
                      [p := transform_mt_90 * p for _ in range(3)])
        elif symmetry == 'NO':
            points = [point(*[random.randint(0, size - 1) for _ in range(2)])]
        else:
            raise Exception(f"Symmetry {symmetry} is not supported")
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
                raise Exception("all_checked=False not supported")
        if regen_points:
            for x, y, *_ in points:
                pane.set(x, y, 0, clone=False)
            blacks_num -= len(points)
    return pane


def get_all_checked_words_layout(grid: FlatMatrix) -> list[list[tuple[int, int, int, int]]]:
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


def create_cross_words_index(words_layout: list[list[tuple[int, int, int, int]]],
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
        for y in range(y_init, y_init + word_len):
            horizontal_words_in_y = horizontal_index[y]
            for horizontal_word_in_y in horizontal_words_in_y:
                hw_i_x = horizontal_word_in_y.x_init
                hw_len = horizontal_word_in_y.word_len
                if hw_i_x <= x_init < hw_i_x + hw_len:
                    vertical_word_intersect_pos = y - y_init
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

    def _get_all_checked_words_layout(self,
                                      grid: FlatMatrix) -> list[list[tuple[int, int, int, int]]]:
        return get_all_checked_words_layout(grid)

    def _create_cross_words_index(self,
                                  words_layout: list[list[tuple[int, int, int, int]]],
                                  grid: FlatMatrix) -> tuple[list[WordLayout], list[WordLayout]]:
        return create_cross_words_index(words_layout, grid)

    @property
    def letters_matrix(self) -> FlatMatrix:
        width, height = self.grid.size
        res = FlatMatrix(width=width, height=height)
        for word_layout in self.all:
            if word_layout.direction == WordDirection.VERTICAL:
                for y in range(word_layout.y_init, word_layout.y_init + word_layout.word_len):
                    res.set(word_layout.x_init, y,
                            val=word_layout.word_letters[y - word_layout.y_init],
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
