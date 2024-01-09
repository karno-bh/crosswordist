import random
from karnobh.crosswordist.affine_2d import FlatMatrix, translate, ROT_INT_90, point


def create_grid(size, black_ratio=1/6, all_checked=True, symmetry='X',
                min_word_size=3):
    inc_vectors = [-1 + 0j, 1 + 0j, 0 - 1j, 0 + 1j]
    transform_mt = translate(size - 1, 0) * ROT_INT_90
    pane = FlatMatrix(size, size)
    max_blacks = int(size * size * black_ratio)
    blacks_num = 0
    while blacks_num <= max_blacks:
        regen_points = False
        points = ([p := point(*[random.randint(0, size - 1) for _ in range(2)])] +
                  [p := transform_mt * p for _ in range(3)])
        for x, y, *_ in points:
            if pane.get(x, y) != 0:
                regen_points = True
                break
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
        if not regen_points:
            for x, y, *_ in points:
                pane.set(x, y, 1, clone=False)
            blacks_num += len(points)
    return pane
