import itertools
import random
from dataclasses import dataclass
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
    _mapping: dict[int, str]

    def __init__(self, word_num, direction, x_init, y_init, word_len):
        # super().__init__()
        self.word_num = word_num
        self.direction = direction
        self.x_init = x_init
        self.y_init = y_init
        self.word_len = word_len
        self.word_letters = [""] * self.word_len
        self.word_intersects = [()] * self.word_len
        self._filled_letters = 0
        self._mapping = {}

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

        return (f"WordLayout({self.word_num}, {'H' if self.direction == WordDirection.HORIZONTAL else 'V'}, {self.x_init}, "
                f"{self.y_init}, {self.word_len}, {self.word_letters}, {word_intersects_repr})")

    # def __del__(self):
    #     for i in range(len(self.word_intersects)):
    #         self.word_intersects[i] = None

    def set_letter(self, letter: str, index: int, propagate=True):
        # if len(letter) > 1:
        #     raise Exception("Letter len cannot be greater than 1")
        if letter == "" and self.word_letters[index] != "" and self._filled_letters >= 0:
            self._filled_letters -= 1
            self.word_letters[index] = letter
            del self._mapping[index]
        else:
            if self.word_letters[index] == "":
                self.word_letters[index] = letter
                self._mapping[index] = letter
                self._filled_letters += 1
                # if self._filled_letters > self.word_len:
                #     raise Exception(f"Error in filled letters: {self}, {self.filled_letters}")
            elif self.word_letters[index] != letter:
                raise Exception(f"There is already letter '{self.word_letters[index]}' "
                                f"at index {index}. Trying to set letter '{letter}'. {self}")
        if propagate:
            crossing_word_layout, crossing_word_index = self.word_intersects[index]
            crossing_word_layout.set_letter(letter, crossing_word_index, propagate=False)

    def set_word(self, word):
        for i, l in enumerate(word):
            self.set_letter(l, i)

    def unset_word(self, prev_state):
        # print(f"Unset called: {prev_state} === {self}")
        # for i in range(len(self.word_letters)):
        #     self.set_letter("", i)
        for i, l in enumerate(prev_state):
            if l == '':
                self.set_letter('', i)

    @property
    def filled_letters(self):
        # return self._filled_letters
        return sum(1 for l in self.word_letters if l != '')
        # return len(self._mapping)

    @property
    def mapping(self):
        return {i: l for i, l in enumerate(self.word_letters) if l}
        # return self._mapping

    @property
    def full(self):
        return self.filled_letters == self.word_len


@dataclass
class CrossWordsIndex:
    horizontal_words: list[WordLayout]
    vertical_words: list[WordLayout]

    @property
    def all(self):
        return itertools.chain(self.horizontal_words, self.vertical_words)


def create_random_grid(size, black_ratio=1 / 6, all_checked=True, symmetry='X',
                       min_word_size=3):
    inc_vectors = [-1 + 0j, 1 + 0j, 0 - 1j, 0 + 1j]
    transform_mt_90 = translate(size - 1, 0) * ROT_INT_90
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


def get_all_checked_words_layout(grid: FlatMatrix) -> list[list[tuple]]:
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


def create_cross_words_index(words_layout: list[list[tuple]], grid: FlatMatrix):
    width, height = grid.size
    vertical_index, horizontal_index = [[] for _ in range(width)], [[] for _ in range(height)]
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
    # print("vertical index = ", vertical_index)
    # print("horizontal index = ", horizontal_index)
    # print("vertical words = ", vertical_words)
    # print("horizontal words = ", horizontal_words)

    for vertical_word in vertical_words:
        # _, x_init, y_init, word_len, word_num = vertical_word
        y_init = vertical_word.y_init
        x_init = vertical_word.x_init
        word_len = vertical_word.word_len
        for y in range(y_init, y_init + word_len):
            horizontal_words_in_y = horizontal_index[y]
            for horizontal_word_in_y in horizontal_words_in_y:
                # _, hw_i_x, hw_i_y, hw_len, hw_n = horizontal_word_in_y
                hw_i_x = horizontal_word_in_y.x_init
                hw_len = horizontal_word_in_y.word_len
                if hw_i_x <= x_init < hw_i_x + hw_len:
                    # print(f"Vertical word {vertical_word} intersects {horizontal_word_in_y} "
                    #       f"at y = {y}, horizontal word pos: {x_init - hw_i_x}")
                    vertical_word_intersect_pos = y - y_init
                    horizontal_word_intersect_pos = x_init - hw_i_x
                    vertical_word.word_intersects[vertical_word_intersect_pos] = (horizontal_word_in_y, horizontal_word_intersect_pos)
                    horizontal_word_in_y.word_intersects[horizontal_word_intersect_pos] = (vertical_word, vertical_word_intersect_pos)
                    break
    # print("=========================")
    # for word in vertical_words:
    #     print("Vertical word: ", word)
    # for word in horizontal_words:
    #     print("Horizontal word: ", word)

    return CrossWordsIndex(
        horizontal_words=horizontal_words,
        vertical_words=vertical_words
    )
