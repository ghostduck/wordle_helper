#!/usr/bin/python3

# Debug import problem
#import pprint
#import sys
#pprint.pprint(sys.path)

import pytest
from wordle_helper.wordle_game_check_helper import wordle_game_rule_check

# Verify the real test cases
def test_other_testcases(real_cases_with_answer):
    correct_word, attempts_record = real_cases_with_answer
    for guess, output in attempts_record:
        assert wordle_game_rule_check(guess, correct_word) == output

def test_created_cases(quick_cases_with_answer):
    correct_word, attempts_record = quick_cases_with_answer
    for guess, output in attempts_record:
        assert wordle_game_rule_check(guess, correct_word) == output
