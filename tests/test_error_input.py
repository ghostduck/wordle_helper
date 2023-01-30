#!/usr/bin/python3

# Debug import problem
#import pprint
#import sys
#pprint.pprint(sys.path)

import pytest
from wordle_helper.wordle_no_spoiler_helper import process_all_hints

# Verify the real test cases
def test_other_testcases(error_cases):
    _, attempts_record = error_cases
    with pytest.raises(ValueError):
        process_all_hints(attempts_record)
