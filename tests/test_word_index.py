import karnobh.crosswordist.log_config as log_config
log_config.set_logger()

import unittest
import logging
from karnobh.crosswordist.words_index import WordsIndex

logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):

    def test_something(self):
        logger.warning("Hello from logger of tests")
        wi = WordsIndex()
        wi.add_word()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
