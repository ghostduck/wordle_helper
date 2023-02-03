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

# silly case - waste an attempt, but still a valid hard mode input
# Add this case since previous logic would reject this as hard mode - multiple letter case
silly_test = (
    # correct answer: SCOLD
    ("CROSS","YWGYW"),
    ("CROSS","YWGYW"),
)

# Made it contains 3 tuples
silly_test2 = silly_test + (("CHOSS","YWGYW"),)

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
@pytest.mark.parametrize("normal_case",
    [
        ("rupee_case"),
    ]
)
def test_normal_add_info_cases_from_fixtures(normal_case, request):
    normal_case = request.getfixturevalue(normal_case)

    # By real test cases are all in hard mode
    _, extra_info = process_all_hints(normal_case)

    assert extra_info["is_hard_mode_compatible"] == True
    assert extra_info["is_normal_wordle_game"] == True

@pytest.mark.parametrize("normal_super_hard_case",
    [
        ("flair_case"),  # Failed at FAIRY guess
        ("rupee_case"),  # Failed at CREPE guess
        ("silly_cross_case"),
    ]
)
def test_add_info_failed_super_hard_from_fixtures(normal_super_hard_case, request):
    normal_super_hard_case = request.getfixturevalue(normal_super_hard_case)

    # By real test cases are all in hard mode
    _, extra_info = process_all_hints(normal_super_hard_case)

    assert extra_info["is_hard_mode_compatible"] == True
    assert extra_info["is_super_hard_mode_compatible"] == False
    assert extra_info["is_normal_wordle_game"] == True


@pytest.mark.parametrize("normal_super_hard_case",
    [
        ("robin_case"),
    ]
)
def test_add_info_normal_super_hard_from_fixtures(normal_super_hard_case, request):
    normal_super_hard_case = request.getfixturevalue(normal_super_hard_case)

    # By real test cases are all in hard mode
    _, extra_info = process_all_hints(normal_super_hard_case)

    assert extra_info["is_super_hard_mode_compatible"] == True
    assert extra_info["is_normal_wordle_game"] == True

@pytest.mark.parametrize("normal_case",
    [
        (silly_test),
        (silly_test2),
    ],
    ids=["silly_waste_chance", "silly2"]
)
def test_normal_add_info_cases(normal_case):
    _, extra_info = process_all_hints(normal_case)

    assert extra_info["is_hard_mode_compatible"] == True
    assert extra_info["is_normal_wordle_game"] == True


def test_normal_letters_for_blind_guess_cases(silly_cross_case):
    _, extra_info = process_all_hints(silly_cross_case)

    assert "S" not in extra_info["letters_for_unknown_guess"]
