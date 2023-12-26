import karnobh.crosswordist.log_config as log_config
log_config.set_logger()

import unittest
import logging

from karnobh.crosswordist.bitmap import and_all
from karnobh.crosswordist.bitmap import bit_index
from karnobh.crosswordist.words_index import WordsIndexSameLen

logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.words = [
            "AAA",
            "AAB",
            "AAC",
            "AAD",
            "AAF",
            "AAG",
            "AAH",
            "AAI",
            "BAA",
        ]

    def test_word_index(self):
        wi = WordsIndexSameLen(3)
        for w in self.words:
            wi.add_word(w)
        wi.make_index()
        actual = []
        for n in bit_index(and_all(wi.index_bitmap(2, 'A'),
                                   wi.index_bitmap(0, 'B'))):
            # print(wi.word_at(n))
            actual.append(wi.word_at(n))

        expected = ["BAA"]
        self.assertEqual(expected, actual)

    def test_word_with_lang_features(self):
        with WordsIndexSameLen.as_context(3) as wi:
            for w in self.words:
                wi.add_word(w)
        actual = [wi[n] for n in bit_index(and_all(wi[2:'A'], wi[0:'B']))]
        expected = ["BAA"]
        self.assertEqual(expected, actual)

    def test_word_index_all_selected(self):
        with WordsIndexSameLen.as_context(3) as wi:
            for w in self.words:
                wi.add_word(w)
        actual = [wi[n] for n in bit_index(wi[1:'A'])]
        expected = sorted(self.words)
        self.assertEqual(expected, actual)

    def test_word_index_wrong_len_init(self):
        self.assertRaises(WordsIndexSameLen.WordsIndexWrongLen, WordsIndexSameLen, 1)

    def test_word_index_wrong_len_add(self):
        wi = WordsIndexSameLen(3)
        self.assertRaises(WordsIndexSameLen.WordsIndexWrongLen, wi.add_word, "HELLO")

    def test_word_index_not_from_abc(self):
        wi = WordsIndexSameLen(3)
        actual = wi.add_word("123")
        self.assertEqual(False, actual)

    def test_word_index_wrong_requested_item(self):
        wi = WordsIndexSameLen(3)
        self.assertRaises(WordsIndexSameLen.NotSupportTypeItem, lambda: wi['dd'])
