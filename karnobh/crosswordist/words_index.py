from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class WordsIndex(ABC):

    def __init__(self):
        super().__init__()

    def add_line(self):
        logger.debug("This is a test log message: %s", 42)

