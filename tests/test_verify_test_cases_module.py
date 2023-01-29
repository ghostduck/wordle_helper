#!/usr/bin/python3

# Debug import problem
#import pprint
#import sys
#pprint.pprint(sys.path)

import pytest
from wordle_helper.wordle_game_check_helper import *

# Verify the real test cases
def test_other_testcases(real_cases_with_answer):
    for correct_word, attempts_record in real_cases_with_answer:
        for guess, output in attempts_record:
            assert wordle_game_rule_check(guess, correct_word) == output

def test_created_cases(quick_cases_with_answer):
    for correct_word, attempts_record in quick_cases_with_answer:
        for guess, output in attempts_record:
            assert wordle_game_rule_check(guess, correct_word) == output
