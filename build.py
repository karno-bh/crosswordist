#!/usr/bin/env python3

import subprocess
import sys

this_module = sys.modules[__name__]


def r(cli):
    return subprocess.run(cli, shell=True)


def action_start(text):
    print("===>", text)


def action_end(text):
    print("<===", text)


def action_tests():
    action_start("Running Tests")
    r("python -m coverage run -m unittest")
    action_end("Test passed")


def action_coverage():
    action_start("Running coverage")
    r("python -m coverage report -m")
    action_end("Coverage passed")


def action_linter():
    action_start("Running linter")
    action_start("Running Flake8")
    r("python -m flake8 karnobh/")
    action_end("Flake8 passed")
    action_start("Running pylint")
    r("python -m pylint karnobh/")
    action_end("pylint passed")
    action_start("Running mypy")
    r("python -m mypy karnobh/")
    action_end("mypy passed")
    action_end("Linter passed")


def action_install_req():
    action_start("Install Requirements")
    r("python -m pip install -r dev_requirements.txt")
    action_end("Installing requirements passed")


def action_build():
    action_install_req()
    action_linter()
    action_tests()
    action_coverage()


def main():
    if len(sys.argv) < 2:
        action_str = "build"
    else:
        action_str = sys.argv[1]
    action = getattr(this_module, f"action_{action_str}", None)
    if action is None:
        print(f"Cannot find action: {action_str}")
        exit(1)
    action()


if __name__ == '__main__':
    main()
