import itertools
import random
import time

from karnobh.crosswordist.affine_2d import FlatMatrix
from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.grid_generator import CrossWordsIndex, WordDirection, WordLayout


def _as_flat_matrix(cross_words_index: CrossWordsIndex, orig_grid: FlatMatrix) -> FlatMatrix:
    width, height = orig_grid.size
    res = FlatMatrix(width=width, height=height)
    for word_layout in itertools.chain(cross_words_index.horizontal_words,
                                       cross_words_index.vertical_words):
        if word_layout.direction == WordDirection.VERTICAL:
            # print("vert: ", word_layout)
            # if word_layout.word_num == 7:
            #     print("inside vert: !!!")
            for y in range(word_layout.y_init, word_layout.y_init + word_layout.word_len):
                res.set(word_layout.x_init, y, val=word_layout.word_letters[y - word_layout.y_init],
                        clone=False)
            # if word_layout.word_num == 7:
            #     print("inside vert: ")
            #     print(res.pretty_log({0: "*", "": "_"}))
        elif word_layout.direction == WordDirection.HORIZONTAL:
            # print("horiz: ", word_layout)
            # if word_layout.word_num == 7:
            #     print("inside horiz: !!!")
            for x in range(word_layout.x_init, word_layout.x_init + word_layout.word_len):
                res.set(x, word_layout.y_init, val=word_layout.word_letters[x - word_layout.x_init],
                        clone=False)
            # if word_layout.word_num == 7:
            #     print("inside horiz: ")
            #     print(res.pretty_log({0: "*", "": "_"}))
    return res


def _find_solution(word_index: WordsIndex, cross_words_index: CrossWordsIndex,
                   orig_grid: FlatMatrix,
                   current_word: WordLayout,
                   filled_words: set[tuple[int, WordDirection]],
                   non_filled_words: set[tuple[int, WordDirection]], level=0):
    words_to_check = _get_words_from_index(word_layout=current_word,
                                           word_index=word_index)
    print(_as_flat_matrix(cross_words_index, orig_grid).pretty_log({0: "*", "": "_"}))
    # print("filled words: ", filled_words)
    # print("non filled words: ", non_filled_words)
    for word_to_check in words_to_check:
        current_word.set_word(word_to_check)
        # print(current_word)
        # for w in current_word.word_intersects:
        #     print("  intersect: ", w)
        print("Current word: ", current_word)
        non_filled_intersects = [w for w, _ in current_word.word_intersects
                                 if w.filled_letters != w.word_len]
        print("Non filled intersects: ", non_filled_intersects)
        if not non_filled_intersects:
            print("Current word after non filtered intersects: ", current_word)
            next_word_layout, possibilities = _min_possible_word_layout((w for w, _ in current_word.word_intersects), word_index)
            if possibilities == 0:
                current_word.unset_word()
                continue
            print("Before returning 1")
            print(_as_flat_matrix(cross_words_index, orig_grid).pretty_log({0: "*", "": "_"}))
            found_not_filled = None
            for word_layout in itertools.chain(cross_words_index.horizontal_words,
                                               cross_words_index.vertical_words):
                if word_layout.filled_letters != word_layout.word_len:
                    found_not_filled = word_layout
            print("found not filled", found_not_filled)
            if found_not_filled:
                res = _find_solution(word_index, cross_words_index, orig_grid, found_not_filled, filled_words, non_filled_words)
                print("res = ", res)
            return 1
        print("There are non filtered intersects")
        print("Word sizes: ", [w.filled_letters for w in non_filled_intersects])
        next_word_layout, possibilities = _min_possible_word_layout(non_filled_intersects, word_index)
        print(f"possibilities: {possibilities}, next word layout: {next_word_layout}")
        if possibilities == 0:
            return -1
        # filled_words.add(_as_index_tuple(next_word_layout))
        # non_filled_words.remove(_as_index_tuple(next_word_layout))
        res = _find_solution(word_index, cross_words_index, orig_grid, next_word_layout, filled_words, non_filled_words)
        if res < 0:
            current_word.unset_word()
            # filled_words.remove(_as_index_tuple(next_word_layout))
            # non_filled_words.add(_as_index_tuple(next_word_layout))
        else:
            print("Current word in the end: ", current_word)
            print("Current word intersects: ", current_word.word_intersects)
            return res
    return -1


def _find_solution2(word_index: WordsIndex, cross_words_index: CrossWordsIndex,
                    orig_grid: FlatMatrix,
                    current_word: WordLayout, in_crossword_words, path, start_time):
    words_to_check = _get_words_from_index(word_layout=current_word,
                                           word_index=word_index)
    random.shuffle(words_to_check)
    # print("Path = ", path)
    # print(_as_flat_matrix(cross_words_index, orig_grid).pretty_log({0: "*", "": "_"}))
    # print("filled words: ", filled_words)
    # print("non filled words: ", non_filled_words)
    for word_to_check in words_to_check:
        if word_to_check in in_crossword_words:
            continue
        prev_state = list(current_word.word_letters)
        current_word.set_word(word_to_check)
        words_intersect_not_good = False
        for current_word_intersect in current_word.word_intersects:
            current_word_intersect_layout, _ = current_word_intersect
            if _check_possibilities(current_word_intersect_layout, word_index) == 0:
                current_word.unset_word(prev_state)
                words_intersect_not_good = True
                break
        if words_intersect_not_good:
            continue
        next_word_layout, possibilities = _min_possible_word_layout_non_full(cross_words_index.all,
                                                                             word_index)
        if next_word_layout is None:
            # print("Solution: ")
            # print(_as_flat_matrix(cross_words_index, orig_grid).pretty_log({0: "*", "": "_"}))
            return 0
        # next_path = list(path)
        # next_path.append(next_word_layout)
        # print("Next word layout: ", next_word_layout)
        res = _find_solution2(word_index, cross_words_index, orig_grid, next_word_layout,
                              in_crossword_words, path, start_time)
        if res == 0 or res == 2:
            return res
        current_word.unset_word(prev_state)
    if time.time() - start_time > 60:
        print("Timeout: ", time.time() - start_time)
        return 2
    # print(_as_flat_matrix(cross_words_index, orig_grid).pretty_log({0: "*", "": "_"}))
    return 1


def _get_words_from_index(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return list(word_index.lookup_native(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        ))
    else:
        return list(word_index.word_index_by_length(word_layout.word_len))


def _check_possibilities(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return len(list(word_index.lookup_native(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        )))
    else:
        return len(word_index.word_index_by_length(word_layout.word_len).words)


def _as_index_tuple(word_layout: WordLayout) -> tuple[int, WordDirection]:
    return (word_layout.word_num, word_layout.direction)


def _min_possible_word_layout(word_layouts, word_index: WordsIndex):
    return min(((w, _check_possibilities(w, word_index)) for w in word_layouts),
               key=lambda _wp: _wp[1])


def _min_possible_word_layout_non_full(word_layouts, word_index: WordsIndex):
    layouts_with_possibilities = [(w, _check_possibilities(w, word_index)) for w in word_layouts if not w.full]
    if not layouts_with_possibilities:
        return None, -1
    return min(layouts_with_possibilities, key=lambda _wp: _wp[1])


def random_possible_word_layout(word_layouts, word_index: WordsIndex):
    word_layouts = [(w, _check_possibilities(w, word_index)) for w in word_layouts if not w.full]
    return random.choice(word_layouts)


def find_solution(word_index: WordsIndex, cross_words_index: CrossWordsIndex,
                  orig_grid: FlatMatrix):
    non_filled_words = {_as_index_tuple(w) for w in itertools.chain(
        cross_words_index.horizontal_words, cross_words_index.vertical_words)}
    filled_words = set()
    # for w in itertools.chain(
    #         cross_words_index.horizontal_words, cross_words_index.vertical_words):
    #     print(_check_possibilities(w, word_index))
    # start_word_layout = min((w for w in itertools.chain(cross_words_index.horizontal_words,
    #                                                     cross_words_index.vertical_words)),
    #                         key=lambda _w: _check_possibilities(_w, word_index))
    start_word_layout, possibilities = _min_possible_word_layout_non_full(cross_words_index.all, word_index)
    print("possibilities", possibilities)
    non_filled_words.remove(_as_index_tuple(start_word_layout))
    filled_words.add(_as_index_tuple(start_word_layout))
    return _find_solution(word_index, cross_words_index,
                          orig_grid,
                          start_word_layout,
                          filled_words, non_filled_words)


def find_solution2(word_index: WordsIndex, cross_words_index: CrossWordsIndex,
                   orig_grid: FlatMatrix):
    # non_filled_words = {_as_index_tuple(w) for w in itertools.chain(
    #     cross_words_index.horizontal_words, cross_words_index.vertical_words)}
    # filled_words = set()
    # for w in itertools.chain(
    #         cross_words_index.horizontal_words, cross_words_index.vertical_words):
    #     print(_check_possibilities(w, word_index))
    # start_word_layout = min((w for w in itertools.chain(cross_words_index.horizontal_words,
    #                                                     cross_words_index.vertical_words)),
    #                         key=lambda _w: _check_possibilities(_w, word_index))
    # for _ in range(5):
    next_word_layout, possibilities = _min_possible_word_layout_non_full(cross_words_index.all,
                                                                         word_index)
    # print("possibilities", possibilities)
    in_crossword_words = {}
    path = [next_word_layout]
    return _find_solution2(word_index, cross_words_index,
                           orig_grid,
                           next_word_layout, in_crossword_words, path, time.time())
    # if res == 1 or res == 0:
    #     return res
    # print("==== Regenerating ====")
