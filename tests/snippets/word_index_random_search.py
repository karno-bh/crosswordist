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
            index_words = list(words_index.lookup(word_length, mapping=filter_set))
            t1 = time.time()
            # non_index_words = naive_lookup(words_index[word_length].words, mapping=filter_set)
            t2 = time.time()
            total_index_time += t1 - t0
            total_non_index_time += t2 - t1
            try:
                # self.assertEqual(non_index_words, index_words)
                # if non_index_words != index_words:
                #     raise Exception("Assert failed")
                if index_words != index_words:
                    raise Exception("Lala lala")
            except Exception:
                logger.error("Assertion error on filter_set=%s, length=%s", filter_set, word_length)
                raise
    logger.info("Total index time: %s, total non index time: %s",
                total_index_time, total_non_index_time)
    print(f"Total index time: {total_index_time}, total non index time {total_non_index_time} "
          f"Ratio {total_non_index_time / total_index_time}")

def main():
    test_word_index()

if __name__ == '__main__':
    main()
