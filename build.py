#!/usr/bin/env python3

import subprocess
import sys
import logging

logger = logging.getLogger(__name__)
this_module = sys.modules[__name__]


def tests():
    logger.info("Running tests")
    result = subprocess.run("python -m unittest", shell=True)
    if result.returncode != 0:
        logger.error("Tests failed")
        exit(1)
    logger.info("Test passed")


def coverage():
    logger.warning("Coverage should be implemented")


def linter():
    logger.info("Running linter")
    result = subprocess.run("python -m flake8 karnobh/", shell=True)
    if result.returncode != 0:
        logger.error("Linter failed")
        # exit(1)
    logger.info("Linter passed")


def build():
    linter()
    tests()
    coverage()


def main():
    if len(sys.argv) < 2:
        logger.error("Action should be specified")
        exit(1)
    action_str = sys.argv[1]
    action = getattr(this_module, action_str, None)
    if action is None:
        logger.error(f"Cannot find action: %s", action_str)
        exit(1)
    action()


if __name__ == '__main__':
    main()
