#!/usr/bin/python3

# Debug import problem
import pprint
import sys
pprint.pprint(sys.path)

import pytest


def get_test_file_full_path(request, rel_path):
    # ugly hack on PATH problem
    # Get hints from https://stackoverflow.com/questions/50815777/parametrize-the-test-based-on-the-list-test-data-from-a-json-file

    # Tried these:
    # request.node.fspath.strpath   - "/full/path/to/tests/conftest.py"
    # request.node.fspath.dirpath() - /full/path/to/tests , without the closing '/'

    # Strangely enough I cannot use request.node.fspath.dirpath() + "/" to form the path. The '/' will be removed
    # But it works for str(request.node.fspath.dirpath()) + "/"
    dir_full_path = str(request.node.fspath.dirpath()) + "/"
    return dir_full_path + rel_path


@pytest.fixture
def real_cases_with_answer(request):
    rela_path_to_file = "test_cases/cases_with_answer/real_cases.txt"
    full_path = get_test_file_full_path(request, rela_path_to_file)

    return read_cases_with_answers_from_file(full_path)

@pytest.fixture
def quick_cases_with_answer(request):
    rela_path_to_file = "test_cases/cases_with_answer/quick_cases.txt"
    full_path = get_test_file_full_path(request, rela_path_to_file)

    return read_cases_with_answers_from_file(full_path)


def read_cases_with_answers_from_file(path):
    list_of_cases = []
    answer = None
    guesses = ()

    # each case is a tuple of 2 items - string of "correct word" (answer), tuple of many guesses
    # The tuple is like a list. It contains many pairs of guessed word and results

    # Example of an item:
    # list_of_cases[0] = (
    #    "RUPEE",(
    #        ("PRIDE", "YYWWG"),
    #        ("SPARE", "WYWYG"),
    #        ...
    #    )
    # )

    with open(path) as file:
        for line in file:

            line = line.strip()

            # skip comment line and blank line
            if (bool(line) and not line.startswith("#")):

                # answer defining line - Also treated as a new case
                if line.startswith("="):

                    # some valid cases before
                    if answer is not None and bool(guesses):

                        # add existing valid cases, then clean everything up for new case
                        list_of_cases.append((answer, guesses))
                        guesses = ()  # just like guesses.clear() but it is a tuple
                        answer = ""

                    answer = line[1:]

                else:
                    # assume to be guesses line
                    guess_word, outcome = line.split()
                    if not (len(guess_word) == len(outcome) == len(answer)):
                        raise ValueError("guess_word, outcome and answer not having same length. {} - {} - {}".format(guess_word, outcome, answer))
                    guesses += ((guess_word, outcome),)

    # Finish reading file
    # Too bad I have to repeat myself ...
    if answer is not None and bool(guesses):
        list_of_cases.append((answer, guesses))

    return list_of_cases
