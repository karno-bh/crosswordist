"""
This module is responsible for finding solution in provided Word Index and Cross Words Index.
Word Index is the index of all available words.
Cross Words Index is graph of vertical and horizontal words with their crossings.
"""
import random
import time
from enum import Enum

from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.grid_generator import CrossWordsIndex, WordLayout


class FinderResult(Enum):
    """
    Possible values for the finding algorithm result
    """
    FOUND = 0
    NO_SOLUTION = 1
    TIMED_OUT = 2


def _get_words_from_index(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return list(word_index.lookup(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        ))
    return list(word_index.word_index_by_length(word_layout.word_len))


def _check_possibilities(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return word_index.count_occurrences(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        )
    return len(word_index.word_index_by_length(word_layout.word_len).words)


def _has_possibility(word_layout: WordLayout, word_index: WordsIndex):
    if word_layout.filled_letters:
        return word_index.does_intersection_exist(
            length=word_layout.word_len,
            mapping=word_layout.mapping
        )
    return len(word_index.word_index_by_length(word_layout.word_len).words) != 0


def _min_possible_word_layout_non_full(word_layouts, word_index: WordsIndex):
    layouts_with_possibilities = [(w, _check_possibilities(w, word_index))
                                  for w in word_layouts if not w.full]
    if not layouts_with_possibilities:
        return None
    return min(layouts_with_possibilities, key=lambda _wp: _wp[1])[0]


def find_solution(word_index: WordsIndex,
                  cross_words_index: CrossWordsIndex,
                  timeout_after_seconds: float) -> FinderResult:
    """
    This is the main function which is responsible for finding words in the provided index and
    words' graph of a crossword's grid.

    The algorithm mutates a provided graph and the actual solution will be the graph itself
    after the execution.

    Overall, the algorithm finds the next non-fully filled word from all available words in
    crossword graph with the lowest number of possibilities for substitutions. This is important
    because it significantly reduces the number of permutations. If no such word cannot be found it
    means that a solution found (there is no possibility for substitution for the words which are
    not fully filled). It says that a solution found because the algorithm does not allow to
    substitute words which are not in the available words (will be explained later). After some
    non-fully filled word with the lowest number of possibilities found, all possible permutations
    are randomly shuffled. Then the algorithms tries to substitute a word from the shuffled
    collection. If the substituted word does not break a crossword in the meaning that crossing
    words can have some possible substitutions then this word is set and the process of finding the
    next non-fully filled word from all available words in crossword graph continues. First, the
    check that the word does not break crossword in general never leaves the crossword in situation
    where bad variants are considered. Second, this is necessary condition that allows for algorithm
    to determine if a solution found. Checking the words from all possible words from crossword
    graph allows not to use some special techniques to determine if there are some isolated
    "islands" of words because sooner or later the algorithm will come to these "islands" because
    all other parts of a crossword were solved.

    :param word_index: The index of all words.
    :param cross_words_index: The index (or graph) of all crossing words in a graph
    :param timeout_after_seconds: The time in seconds that the algorthm drops its execution
    :return: One of the possible results: Solution found, No solution, Timed out
    """
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
            if res in (FinderResult.FOUND, FinderResult.TIMED_OUT):
                return res
            current_word.set_word(prev_state)
        if time.time() - start_time > timeout_after_seconds:
            return FinderResult.TIMED_OUT
        return FinderResult.NO_SOLUTION

    next_word_layout = _min_possible_word_layout_non_full(cross_words_index.all,
                                                          word_index)
    in_crossword_words: set[str] = set()
    start_time = time.time()
    return _find_solution(next_word_layout)
