import logging
import random
import time

logger = logging.getLogger(__name__)

from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.naive_lookup import  naive_lookup


def test_word_index():

    with open('/tmp/words_tests/index.json') as f:
        words_index = WordsIndex(file=f)
    abc = 'ABCDEFGHIGKLMNOPQRSTUVWXYZ'
    total_index_time = 0
    total_non_index_time = 0
    found_words = 0
    empty_findings = 0
    non_empty_findings = 0
    for i in range(30000):
        if i % 100 == 0:
            ratio = 0 if total_index_time == 0 else total_non_index_time / total_index_time
            print(f"i = {i}; total_index_time = {total_index_time}; "
                  f"total_non_index_time = {total_non_index_time}; ratio = {ratio}")
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
            # non_index_words = list(words_index.lookup(word_length, mapping=filter_set))
            t1 = time.time()
            # non_index_words = naive_lookup(words_index[word_length].words, mapping=filter_set)
            non_index_words = list(words_index.lookup(word_length, mapping=filter_set))
            t2 = time.time()
            found_words += len(index_words)
            if not index_words:
                empty_findings += 1
            else:
                non_empty_findings += 1
            total_index_time += t1 - t0
            total_non_index_time += t2 - t1
            try:
                # self.assertEqual(non_index_words, index_words)
                if non_index_words != index_words:
                    raise Exception("Assert failed")
                else:
                    # print("=== OK ====")
                    pass
                # if index_words != index_words:
                #     raise Exception("Lala lala")
            except Exception:
                logger.error("Assertion error on filter_set=%s, length=%s", filter_set, word_length)
                raise
    logger.info("Total index time: %s, total non index time: %s",
                total_index_time, total_non_index_time)
    print(f"Total index time: {total_index_time}, total non index time {total_non_index_time} "
          f"Ratio {total_non_index_time / total_index_time}")
    print("Found words: ", found_words, " empty findings: ", empty_findings,
          " non empty findings: ", non_empty_findings, "::: total", empty_findings + non_empty_findings)

def test_concrete():
    mapping = {0: 'T', 2: 'C'}
    # mapping = {2: 'C'}
    length = 4
    # mapping = {0: 'B', 1: 'A'}
    # length = 19
    with open('/home/serj/programming/research/python/crosswordist/tests/assets/random_filtered_words_idx.json') as f:
        words_index = WordsIndex(file=f)
    print(words_index[length].words, len(words_index[length].words))
    # index_words = list(words_index.lookup_native(length, mapping=mapping))
    index_words = list(words_index.lookup(length, mapping=mapping))
    print(index_words)
    print("==== NATIVE ====")
    index_words = list(words_index.lookup_native(length, mapping=mapping))
    print(index_words)


def main():
    test_word_index()
    # test_concrete()


if __name__ == '__main__':
    main()
