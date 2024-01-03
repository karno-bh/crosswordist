import operator

import karnobh.crosswordist.log_config as log_config
log_config.set_logger()

import unittest
import logging

from karnobh.crosswordist.bitmap import and_all
from karnobh.crosswordist.bitmap import bit_index, bit_op_index2
from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)

logger = logging.getLogger(__name__)


class WordIndexSameLengthTestCase(unittest.TestCase):

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
        for n in bit_index(and_all(wi.bitmap_on_position(2, 'A'),
                                   wi.bitmap_on_position(0, 'B'))):
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

    def test_word_with_lang_features_bit_op2(self):
        with WordsIndexSameLen.as_context(3) as wi:
            for w in self.words:
                wi.add_word(w)
        actual = [wi[n] for n in bit_op_index2(wi[2:'A'], wi[0:'B'], op=operator.and_)]
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
        self.assertRaises(WordsIndexWrongLen, WordsIndexSameLen, 1)

    def test_word_index_wrong_len_add(self):
        wi = WordsIndexSameLen(3)
        self.assertRaises(WordsIndexWrongLen, wi.add_word, "HELLO")

    def test_word_index_not_from_abc(self):
        wi = WordsIndexSameLen(3)
        actual = wi.add_word("123")
        self.assertEqual(False, actual)

    def test_word_index_wrong_requested_item(self):
        wi = WordsIndexSameLen(3)
        self.assertRaises(NotSupportTypeItem, lambda: wi['dd'])


class WordIndexTestCase(unittest.TestCase):

    def test_corpus_loading(self):
        pass
        # with open('/tmp/words_tests/words_upper.txt') as f:
        #     with WordsIndex.as_context() as wi:
        #         for word in f:
        #             wi.add_word(word.strip())
