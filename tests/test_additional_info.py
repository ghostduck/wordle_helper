#!/usr/bin/python3

# Debug import problem
#import pprint
#import sys
#pprint.pprint(sys.path)

import pytest
from wordle_helper.wordle_no_spoiler_helper import process_all_hints

# length of 6
school_test = [
    ("WORDLE", "WYWWYW"),
]

# edit from ROBIN case
non_hard_test = [
    ("PRIDE", "WYYWW"),
    ("NYMPH", "YWWWW"),
]

@pytest.mark.parametrize("not_normal_wordle_input", [
    (school_test),
],
ids=["NOT_NORMAL_SCHOOL"])
def test_not_normal_wordle_cases(not_normal_wordle_input):
    _, extra_info = process_all_hints(not_normal_wordle_input)

    assert extra_info["is_normal_wordle_game"] == False

@pytest.mark.parametrize("not_hard_mode_wordle_input", [
    (non_hard_test),
],
ids=["NOT_HARD_MODE_CHECK"])
def test_not_hard_mode_cases(not_hard_mode_wordle_input):
    _, extra_info = process_all_hints(not_hard_mode_wordle_input)

    assert extra_info["is_hard_mode_compatible"] == False


# Workaround to re-use fixture in parametrize by using request and request.getfixturevalue()
# Reference: https://miguendes.me/how-to-use-fixtures-as-arguments-in-pytestmarkparametrize
@pytest.mark.parametrize(
    "normal_case",
    [
        ("rupee_case"),
    ]
)
def test_normal_add_info_cases(normal_case, request):
    normal_case = request.getfixturevalue(normal_case)

    # By real test cases are all in hard mode
    _, extra_info = process_all_hints(normal_case)

    assert extra_info["is_hard_mode_compatible"] == True
    assert extra_info["is_normal_wordle_game"] == True
