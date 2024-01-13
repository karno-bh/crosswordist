import cProfile
import karnobh.crosswordist.log_config as log_config
log_config.LOGGING_CONFIG['loggers']['karnobh.crosswordist']['level'] = 'INFO'
log_config.set_logger()

from karnobh.crosswordist.words_index import (WordsIndexSameLen, WordsIndexWrongLen,
                                              NotSupportTypeItem, WordsIndex)
from karnobh.crosswordist.bitmap import bit_index, bit_op_index2
import operator


def run_load():
    with open('/tmp/words_tests/words_upper.txt') as f:
        with WordsIndex.as_context() as wi:
            for word in f:
                wi.add_word(word.strip())
    # with open('/tmp/words_tests/index.json', 'w') as f:
    #     wi.dump(f)
    # with open('/tmp/words_tests/index.json') as f:
    #     wi_loaded = WordsIndex(file=f)
    # words24 = wi_loaded[24]
    # for n in bit_op_index2(words24[0:'A'], words24[3:'A'], op=operator.and_):
    #     print(words24[n])
    # for word in wi_loaded.lookup(7, {0: 'E', 1: 'P', 6: 'A'}):
    #     print(word)


if __name__ == '__main__':
    run_load()
