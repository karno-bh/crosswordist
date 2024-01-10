import cProfile
import random

import karnobh.crosswordist.log_config as log_config
log_config.LOGGING_CONFIG['loggers']['karnobh.crosswordist']['level'] = 'INFO'
log_config.set_logger()

from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)


def save_part_of_corpus():
    with open('/tmp/words_tests/index.json') as f:
        wi_loaded = WordsIndex(file=f)
    with open('/tmp/words_tests/random_filtered_words.txt', 'w') as f:
        for word_length in range(3, 8):
            length_word_index = wi_loaded.word_index_by_length(word_length)
            for word in length_word_index.words:
                if random.randint(0, 9) == 0:
                    print(word, file=f)


def main():
    save_part_of_corpus()


if __name__ == '__main__':
    main()
