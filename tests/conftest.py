#!/usr/bin/python3

# Debug import problem
import pprint
import sys
pprint.pprint(sys.path)

import pytest

# The second boolean means that first line of "=" is description if True
fixture_mapping = [
    ("real_cases_with_answer",False,"test_cases/cases_with_answer/real_cases.txt"),
    ("quick_cases_with_answer",False,"test_cases/cases_with_answer/quick_cases.txt"),
    ("error_cases",True,"test_cases/cases_without_answer/error_cases.txt")
]


def pytest_generate_tests(metafunc):
    # Assume running the test from top-level in directory, so "tests/test_cases/..." is readable
    for fixture_name, isDes, fixture_path in fixture_mapping:
        if fixture_name in metafunc.fixturenames:
            metafunc.parametrize(fixture_name, read_cases_with_answers_from_file("tests/" + fixture_path, isDescription=isDes), ids=get_real_case_id)

def get_real_case_id(t):
    # t = ("correct answer", (guesses))
    # Like a static varible in C
    try:
        get_real_case_id.case_counter += 1
    except AttributeError:
        get_real_case_id.case_counter = 1

    return str(get_real_case_id.case_counter) + ":" + t[0]

@pytest.fixture
def rupee_case(request):
    return [
        # Possible patterns: REP?E, R?PEE
        # P must be at 3rd therefore R at 1st only
        ("PRIDE","YYWWG"),
        ("SPARE","WYWYG"),
        ("CREPE","WYYYG"),
    ]

def read_cases_with_answers_from_file(path, isDescription=False):
    list_of_cases = []
    answer_description = None
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

                # answer/description defining line - Also treated as a new case
                if line.startswith("="):

                    # some valid cases before
                    if answer_description is not None and bool(guesses):

                        # add existing valid cases, then clean everything up for new case
                        list_of_cases.append((answer_description, guesses))
                        guesses = ()  # just like guesses.clear() but it is a tuple
                        answer_description = ""

                    # also can be used as case description
                    answer_description = line[1:].strip()  # use strip to remove meaningless spaces

                else:
                    # assume to be guesses line
                    guess_word, outcome = line.split()
                    if isDescription:
                        # answer field is description - ignore its length
                        if not (len(guess_word) == len(outcome)):
                            raise ValueError("guess_word, outcome not having same length. {} - {} - {}".format(guess_word, outcome))
                        guesses += ((guess_word, outcome),)

                    else:
                        if not (len(guess_word) == len(outcome) == len(answer_description)):
                            raise ValueError("guess_word, outcome and answer not having same length. {} - {} - {}".format(guess_word, outcome, answer_description))
                        guesses += ((guess_word, outcome),)

    # Finish reading file
    # Too bad I have to repeat myself ...
    if answer_description is not None and bool(guesses):
        list_of_cases.append((answer_description, guesses))

    return list_of_cases
