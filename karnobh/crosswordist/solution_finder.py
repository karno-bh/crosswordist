import random
import time
from enum import Enum

from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.grid_generator import CrossWordsIndex, WordLayout


class FinderResult(Enum):
    FOUND = 0
    NO_SOLUTION = 1
    TIMED_OUT = 2


def _get_words_from_index(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return list(word_index.lookup(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        ))
    else:
        return list(word_index.word_index_by_length(word_layout.word_len))


def _check_possibilities(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return word_index.count_occurrences(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        )
    else:
        return len(word_index.word_index_by_length(word_layout.word_len).words)


def _has_possibility(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return word_index.does_intersection_exist(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        )
    else:
        return len(word_index.word_index_by_length(word_layout.word_len).words) != 0


def _min_possible_word_layout_non_full(word_layouts, word_index: WordsIndex):
    layouts_with_possibilities = [(w, _check_possibilities(w, word_index)) for w in word_layouts if not w.full]
    if not layouts_with_possibilities:
        return None
    return min(layouts_with_possibilities, key=lambda _wp: _wp[1])[0]


def find_solution(word_index: WordsIndex,
                  cross_words_index: CrossWordsIndex,
                  timeout_after_seconds: float) -> FinderResult:

    def _find_solution(current_word: WordLayout) -> FinderResult:
        words_to_check = _get_words_from_index(word_layout=current_word,
                                               word_index=word_index)
        random.shuffle(words_to_check)
        for word_to_check in words_to_check:
            if word_to_check in in_crossword_words:
                continue
            # get a copy of the letters
            prev_state = list(current_word.word_letters)
            current_word.set_word(word_to_check)
            words_intersect_not_good = False
            for current_word_intersect in current_word.word_intersects:
                current_word_intersect_layout, _ = current_word_intersect
                if not _has_possibility(current_word_intersect_layout, word_index):
                    current_word.set_word(prev_state)
                    words_intersect_not_good = True
                    break
            if words_intersect_not_good:
                continue
            next_word_layout_inner = _min_possible_word_layout_non_full(cross_words_index.all,
                                                                        word_index)
            if next_word_layout_inner is None:
                return FinderResult.FOUND
            res = _find_solution(next_word_layout_inner)
            if res == FinderResult.FOUND or res == FinderResult.TIMED_OUT:
                return res
            current_word.set_word(prev_state)
        if time.time() - start_time > timeout_after_seconds:
            return FinderResult.TIMED_OUT
        return FinderResult.NO_SOLUTION

    next_word_layout = _min_possible_word_layout_non_full(cross_words_index.all,
                                                          word_index)
    in_crossword_words = {}
    start_time = time.time()
    return _find_solution(next_word_layout)
