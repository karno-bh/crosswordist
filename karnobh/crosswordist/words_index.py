from abc import ABC
from contextlib import contextmanager
import logging


from karnobh.crosswordist.bitmap import CompressedBitmap, bool_to_byte_bits_seq

logger = logging.getLogger(__name__)


class WordsIndexSameLen:

    class WordsIndexWrongLen(Exception):
        pass

    class NotSupportTypeItem(Exception):
        pass

    def __init__(self, length, alphabet=None):
        super().__init__()
        if not isinstance(length, int) or length < 2:
            raise self.WordsIndexWrongLen("The length of word should be integer and at least 2 letters")
        if alphabet is None:
            logger.info("The alphabet is not provided. Latin alphabet will be used.")
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._abc = alphabet

        self._length = length
        self._bitmap_index = None
        self._words = []

    def add_word(self, word) -> bool:
        if len(word) != self._length:
            raise self.WordsIndexWrongLen(f"Word: {word} is not of required length {self._length}")
        if next((ltr for ltr in word if ltr not in self._abc), None) is not None:
            logger.debug("Word %s is not in the abc '%s'", word, self._abc)
            return False
        self._words.append(word)
        return True

    def make_index(self):
        self._words.sort()
        self._bitmap_index = []
        for i in range(self._length):
            letter_index = dict()
            for abc_letter in self._abc:
                abc_letter_bitmap = CompressedBitmap(
                    byte_sequence=bool_to_byte_bits_seq(
                        map(
                            lambda _l: _l == abc_letter,
                            (w[i] for w in self._words)
                        )
                    )
                )
                letter_index[abc_letter] = abc_letter_bitmap
            self._bitmap_index.append(letter_index)

    def index_bitmap(self, letter_index, letter):
        return self._bitmap_index[letter_index][letter]

    def word_at(self, word_index):
        return self._words[word_index]

    def __getitem__(self, item):
        match item:
            case int():
                return self.word_at(item)
            case slice():
                return self.index_bitmap(item.start, item.stop)
            case _:
                raise self.NotSupportTypeItem(f"Type {type(item)} is not supported")

    @staticmethod
    @contextmanager
    def as_context(length):
        words_index = WordsIndexSameLen(length)
        yield words_index
        words_index.make_index()
