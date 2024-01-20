import random
from dataclasses import dataclass
from karnobh.crosswordist.affine_2d import FlatMatrix, translate, ROT_INT_90, point

class WordDirection:
    HORIZONTAL = 0
    VERTICAL = 1

@dataclass(slots=True)
class WordLayout:
    word_num: int
    direction: WordDirection
    x_init: int
    y_init: int
    word_len: int
    word_letters: list[str]
    word_intersects: list[tuple]

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
    vertical_words = []
    horizontal_words = []
    for word_n, word_layout in enumerate(words_layout):
        for pos_word_layout in word_layout:
            word_dir, x_init, y_init, word_len = pos_word_layout
            pos_word_layout += (word_n,)
            if word_dir == WordDirection.VERTICAL:
                vertical_words.append(pos_word_layout)
                vertical_index[x_init].append(pos_word_layout)
            else:
                horizontal_words.append(pos_word_layout)
                horizontal_index[y_init].append(pos_word_layout)
    print("vertical index = ", vertical_index)
    print("horizontal index = ", horizontal_index)
    print("vertical words = ", vertical_words)
    print("horizontal words = ", horizontal_words)

    # for word_layout in words_layout:
    #     for pos_word_layout in word_layout:
    #         word_dir, x_init, y_init, word_len = pos_word_layout
