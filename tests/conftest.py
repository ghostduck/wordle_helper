#!/usr/bin/python3

# Debug import problem
import pprint
import sys
pprint.pprint(sys.path)

import pytest

fixture_mapping = [
    ("real_cases_with_answer", "test_cases/cases_with_answer/real_cases.txt"),
    ("quick_cases_with_answer", "test_cases/cases_with_answer/quick_cases.txt"),
    ("error_cases", "test_cases/cases_without_answer/error_cases.txt")
]


def pytest_generate_tests(metafunc):
    # Assume running the test from top-level in directory, so "tests/test_cases/..." is readable
    for fixture_name, fixture_path in fixture_mapping:
        if fixture_name in metafunc.fixturenames:
            metafunc.parametrize(fixture_name, read_cases_with_answers_from_file("tests/" + fixture_path), ids=get_real_case_id)

def get_real_case_id(t):
    # t = ("correct answer", (guesses))
    # Like a static varible in C
    try:
        get_real_case_id.case_counter += 1
    except AttributeError:
        get_real_case_id.case_counter = 1

    return str(get_real_case_id.case_counter) + "-" + t[0]


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

                    # also can be used as case description
                    answer = line[1:].strip()  # use strip to remove meaningless spaces

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
