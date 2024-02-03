from crosswordist_native_index.compressed_seq import bit_index_native, bit_and_op_index_native
from karnobh.crosswordist.words_index import WordsIndex

_GET_LIST = 0
_GET_COUNT = 1
_DOES_EXIST = 2


class WordIndexNative(WordsIndex):
    def __init__(self, alphabet: list[str] = None, length_range: range = None, file=None):
        super().__init__(alphabet, length_range, file)

    def _perform_lookup(self, length, mapping, op=None, lookup_type=None):
        words_index_same_len = self.word_index_by_length(length)
        max_alloc = len(words_index_same_len.words)
        byte_sequences = [words_index_same_len.bitmap_on_position(pos, letter).compressed_sequence
                          for pos, letter in mapping.items()]
        arr_index_stream = bit_and_op_index_native(byte_sequences, max_alloc, lookup_type) \
            if len(byte_sequences) != 1 else bit_index_native(byte_sequences[0], max_alloc,
                                                              lookup_type)
        return arr_index_stream, words_index_same_len

    def lookup(self, length, mapping, op=None):
        arr_index_stream, words_index_same_len = self._perform_lookup(
            length,
            mapping,
            lookup_type=_GET_LIST
        )
        for arr_index in arr_index_stream:
            yield words_index_same_len._words[arr_index]

    def count_occurrences(self, length, mapping, op=None):
        occurrences, _ = self._perform_lookup(length, mapping, lookup_type=_GET_COUNT)
        return occurrences

    def does_intersection_exist(self, length, mapping, op=None):
        exists, _ = self._perform_lookup(length, mapping, lookup_type=_DOES_EXIST)
        return exists
