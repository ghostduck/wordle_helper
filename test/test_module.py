#!/usr/bin/python3

# Debug import problem
#import pprint
#import sys
#pprint.pprint(sys.path)

import pytest
from wordle_helper.wordle_no_spoiler_helper import *

@pytest.fixture
def real_cases():
    return [
        ("RUPEE", (
            ("PRIDE", "YYWWG"),
            ("SPARE", "WYWYG"),
            ("CREPE", "WYYYG"),
            ("RUPEE", "GGGGG"),
        )),

        ("ROBIN", (
            ("PRIDE", "WYYWW"),
            ("MIRTH", "WYYWW"),
            ("FLAIR", "WWWGY"),
            ("ROBIN", "GGGGG"),
        ))
    ]

@pytest.fixture
def created_cases():
        return [
        ("XXBXX", (
            ("BB???", "YWWWW"),
            # Actually WYWWW is also correct too, but our program will produce YWWWW
        )),

        ("XXBBX", (
            ("BB???", "YYWWW"),
        ))
    ]

def test_other_testcases(real_cases):
    for correct_word, attempts_record in real_cases:
        for guess, output in attempts_record:
            assert wordle_game_rule_check(guess, correct_word) == output

def test_created_cases(created_cases):
    for correct_word, attempts_record in created_cases:
        for guess, output in attempts_record:
            assert wordle_game_rule_check(guess, correct_word) == output
