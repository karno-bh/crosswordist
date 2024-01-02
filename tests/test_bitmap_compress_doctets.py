import unittest
import doctest
import karnobh.crosswordist.bitmap


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(karnobh.crosswordist.bitmap))
    return tests
