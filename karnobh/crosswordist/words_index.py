from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class WordsIndexSameLen:

    class WordsIndexWrongLen(Exception):
        pass

    def __init__(self, length, alphabet=None):
        super().__init__()
        if length is not int or length < 2:
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
        if next((l for l in word if l not in self._abc), None) is None:
            logger.debug("Word %s is not in the abc '%s'", word, self._abc)
            return False
        self._words.append(word)
        return True

    def make_index(self):
        self._words.sort()


class WordsIndex(ABC):

    def __init__(self):
        super().__init__()
        self._words_index: dict[int, list] = dict()  # TODO would it be better a sparse array?

    def add_word(self):
        logger.debug("This is a test log message: %s", 42)

    def make_index(self):
        pass

