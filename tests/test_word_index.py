import json
import operator
import random
import time
import importlib.resources as pkg_res
import io

import karnobh.crosswordist.log_config as log_config
log_config.set_logger()

import unittest
import logging

from karnobh.crosswordist.bitmap import and_all
from karnobh.crosswordist.bitmap import bit_index, bit_op_index2
from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)
from karnobh.crosswordist.naive_lookup import naive_lookup

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


class NaiveIndexTestCase(unittest.TestCase):

    def test_naive_lookup(self):
        words = [
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
        res = naive_lookup(words, {0: 'B', 2: 'A'})
        expected = ['BAA']
        self.assertEqual(expected, res)


class WordIndexTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assets_package = 'tests.assets'
        self.corpus_file = 'random_filtered_words.txt'
        self.index_file = 'random_filtered_words_idx.json'

    def test_corpus_loading(self):
        with pkg_res.open_text(self.assets_package, self.corpus_file) as f:
            with WordsIndex.as_context() as words_index:
                for word in f:
                    words_index.add_word(word.strip())
        with io.StringIO() as str_f:
            words_index.dump(str_f)
            str_f.seek(0)
            created_index = json.load(str_f)
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            expected_index = json.load(f)
        self.assertEqual(expected_index, created_index)

    def test_index_loading(self):
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            words_index = WordsIndex(file=f)
        with io.StringIO() as str_f:
            words_index.dump(str_f)
            str_f.seek(0)
            created_index = json.load(str_f)
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            expected_index = json.load(f)
        self.assertEqual(expected_index, created_index)

    def test_word_index(self):
        with pkg_res.open_text(self.assets_package, self.index_file) as f:
            words_index = WordsIndex(file=f)
        # with open('/tmp/words_tests/index.json') as f:
        #     words_index = WordsIndex(file=f)
        abc = 'ABCDEFGHIGKLMNOPQRSTUVWXYZ'
        total_index_time = 0
        total_non_index_time = 0
        for i in range(1000):
            if i % 100 == 0:
                ratio = 0 if total_index_time == 0 else total_non_index_time / total_index_time
                logger.info("i = %s; total_index_time = %s;"
                            " total_non_index_time = %s; ratio = %s",
                            i, total_index_time, total_non_index_time, ratio)
            for word_length in range(3, 7):
                number_of_letters = random.randint(1, word_length - 1)
                letter_indexes = list(range(word_length))
                random.shuffle(letter_indexes)
                # print(letter_indexes[:number_of_letters])
                actual_letter_indexes = letter_indexes[:number_of_letters]
                filter_set = {k: random.choice(abc) for k in actual_letter_indexes}
                # print(filter_set)
                t0 = time.time()
                index_words = list(words_index.lookup_native(word_length, mapping=filter_set))
                t1 = time.time()
                non_index_words = naive_lookup(words_index[word_length].words, mapping=filter_set)
                t2 = time.time()
                total_index_time += t1 - t0
                total_non_index_time += t2 - t1
                try:
                    self.assertEqual(non_index_words, index_words)
                except AssertionError:
                    logger.error("Assertion error on filter_set=%s, length=%s", filter_set, word_length)
                    raise
        logger.info("Total index time: %s, total non index time: %s",
                    total_index_time, total_non_index_time)

    # def test_for_debug(self):
    #     with pkg_res.open_text(self.assets_package, self.index_file) as f:
    #         words_index = WordsIndex(file=f)
    #
    #     filter_set = {4: 'E', 1: 'D'}
    #     word_length = 5
    #     index_words = list(words_index.lookup(word_length, mapping=filter_set))
    #     non_index_words = naive_lookup(words_index[word_length], mapping=filter_set)
    #     print("index words: ", index_words)
    #     print("non index words: ", non_index_words)
    #     self.assertEqual(index_words, non_index_words)
    #
    # def test_for_debug2(self):
    #     with pkg_res.open_text(self.assets_package, self.index_file) as f:
    #         words_index = WordsIndex(file=f)
    #     filter_set = {1: 'C'}
    #     word_length = 5
    #     index_words = list(words_index.lookup(word_length, mapping=filter_set))
    #     non_index_words = naive_lookup(words_index[word_length], mapping=filter_set)
    #     print("index words: ", index_words)
    #     print("non index words: ", non_index_words)
    #     self.assertEqual(set(index_words), set(non_index_words))
