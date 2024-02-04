"""
This module exists to be a test module for comparisons between the functionality which is based
on some indexing (specifically, it's compressed bitmap index) and this one which is a sequential
search of the word in the list of words (of the same length)
"""


def naive_lookup(same_len_words: list[str], mapping: dict[int, str]) -> list[str]:
    """
    Searches for the suitable words in the list of words by provided mapping
    :param same_len_words: list of words of the same length
    :param mapping: mapping of the position to the needed letter (e.g., 2->A, 3->X == find words
                    from the list of words where on the 2nd place is A and on the 3rd place is X)
    :return: list of the suitable words filtered by provided mapping
    """
    result_words = []
    for word in same_len_words:
        suitable = True
        for letter_index, letter in mapping.items():
            if word[letter_index] != letter:
                suitable = False
                break
        if suitable:
            result_words.append(word)

    return result_words
