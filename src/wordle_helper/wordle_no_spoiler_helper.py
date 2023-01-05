#!/usr/bin/python3

WORDLE_LENGTH = 5
MAX_TRY = 6  # Not strictly enforced here
ALL_UPPER_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class OverallHint:
    """Class for accumulated hints."""
    # list of correct letters and None
    # just treat this as the confimred answer of Wordle you can see on screen
    green_hints: list = field(default_factory=list)

    # yellow/wrong hint about the positions to exclude
    # dict of letter to list of int (positions to exclude)
    y_w_hint_excluded_position: Dict[str, list] = field(default_factory=dict)

    # use to indicate the letters that should not be used for guessing
    wrong_letters: Set[str] =  field(default_factory=set)

    # {"A": (min, max)} # min max refer to the letter count
    letter_min_max_counter: Dict[str, tuple] = field(default_factory=defaultdict)


def letters_to_try(hint) -> list:
    return [l for l in ALL_UPPER_LETTERS if l not in hint.wrong_letters]



def wordle_game_rule_check(guess, answer):
    """Same logic as the Wordle game single round check.
    Return output as string.

    G(Green) - Correct letter and correct position.
    Y(Yellow) - "Generally" correct letter but wrong position.
    W(Wrong) - "Generally" wrong letter. (The black in background case.)

    Check code comment for the special cases (multiple letters).

    Example:
    Input:  guess="CREPE", answer="RUPEE"
    Output: "WYYYG"
    """

    # ---------------------------------------------------------------
    # Consider these multiple-letter-cases:
    # Answer | 1) XXBXX 2) XXBBX
    # Guess  | Output
    # BB???  | 1) YWWWW   2) YYWWW

    # One of the B is yellow - nothing special.
    # Another B is yellow if there are 2 or more 'B's in the correct word.
    # Otherwise (only 1 B) it is black.

    # This shows the output of second B cannot be determined until all the
    # correct letters are confirmed
    # This is also why we cannot decide all the output within a simple loop
    # ---------------------------------------------------------------

    # Setup and sanity check
    guess = guess.upper()
    answer = answer.upper()

    if len(answer) != len(guess):
        raise ValueError("Answer and guess have different length")

    output= [None] * len(answer)

    # for yellow / wrong case
    correct_letter_count = defaultdict(int)  # default value: 0
    y_w_guess_indices = []

    # Handle green hints first
    for i, guess_letter in enumerate(guess):
        correct_letter = answer[i]
        if guess_letter == correct_letter:
            output[i] = "G"
        else:
            # setup data for yellow / wrong case
            correct_letter_count[correct_letter] += 1

            y_w_guess_indices.append(i)

    # Yellow / Wrong hints
    for i in y_w_guess_indices:
        current_guess_letter = guess[i]

        if current_guess_letter not in correct_letter_count:
            # Wrong case, or no more multiple of correct letters within correct_letter_count
            output[i] = "W"
        else:
            # Yellow case - matches non-green letters
            output[i] = "Y"

            if correct_letter_count[current_guess_letter] > 1:
                correct_letter_count[current_guess_letter] -= 1
            else:
                del correct_letter_count[current_guess_letter]

    return "".join(output)


def generate_round_counter_info(guess, guess_result):
    """Return a new dict of letter count based on input of guess and guess_result."""
    # Example of counter:
    #(min/current, max) -> default (1, WORDLE_LENGTH)
    # A (first letter) -> (1,5)
    # ---
    # B (another letter) -> (1,4) , A -> (1,4)
    # A (another A, AA) -> (2,5)
    # ---
    # C (new letter, CBA) -> (1,3), B-> (1,3), -> A(1,3)
    # B (BBA or AAB, 2:1) -> (2,4), (1,3)
    # A (all same letter) -> (3,5)

    # So the rule is:
    # New green or yellow hint
    # - 1. existing same letter: min count of that letter +1
    # - 2. other letters: max - 1
    # - 3. otherwise - create entry for current letter, (1, MAX-len(current_dict))
    # New wrong hint (multiple letter) - must be processed after B/G hint
    # (watch out for case like ???B?, XXBBX, WWWGW)
    # for that letter - max = min (set upper limit)
    # Otherwise (wrong hint, single letter) - add to wrong letter (max length is 0)

    letter_min_max_counters = dict()
    wrong_letters = set()

    # Green/Yellow hints
    letter_used = 0
    gy_gen = (i for i,r in enumerate(guess_result) if r == "G" or r == "Y")

    for i in gy_gen:
        guess_letter = guess[i]

        # counter logic
        if guess_letter not in letter_min_max_counters:
            # 3. create new entry

            # note that len(letter_min_max_counters) is wrong since possible to
            # have multiple letters which leads to fewer entries in the dict
            letter_min_max_counters[guess_letter] = (0, WORDLE_LENGTH - letter_used)

        for k in letter_min_max_counters.keys():
            cur_count, max_count = letter_min_max_counters[k]
            if k == guess_letter:
                # 1. same letter
                letter_min_max_counters[k] = (cur_count+1, max_count)
            else:
                # 2. other letters
                letter_min_max_counters[k] = (cur_count, max_count-1)

        letter_used += 1


    # Wrong hints
    w_gen = (i for i,r in enumerate(guess_result) if r == "W")
    for i in w_gen:
        guess_letter = guess[i]

        if guess_letter in letter_min_max_counters:
            cur_count, max_count = letter_min_max_counters[guess_letter]
            letter_min_max_counters[guess_letter] = (cur_count, cur_count)  # reduce max length to min/current length
        else:
            wrong_letters.add(guess_letter)  # same as max length is 0

    return letter_min_max_counters, wrong_letters



def parse_single_round_hint(guess, guess_result):
    # assume already passed length check

    # some round-hint is invalid - like 4G1Y
    # deal with it?

    current_confirmed_green = [None] * len(guess_result)  # None means UNKNOWN
    y_w_hint_exclude = defaultdict(list)

    # green hints first
    for i, result in enumerate(guess_result):
        guess_letter = guess[i]

        if result == "G":
            current_confirmed_green[i] = guess_letter
        elif result == "Y":
            y_w_hint_exclude[guess_letter].append(i)


        # multiple letter (considering all letters), Yellow -> Hint of minimum amount of letter, and multiple position to exclude
        # single letter, Yellow -> Hint of minimum amount of letter, and position to exclude
        # multiple letter (considering all letters), Wrong -> Tell us the maximum amount of letter, and multiple position to exclude, and should exclude from blind guess
        # single letter, Wrong -> Maximum amount of that letter is 0. Should exclude from blind guess




def parse_hints_from_lines():
    # Green hint: Letter is in correct position
    # Need to remove from free positions

    # Yellow hint: Letter is in the word but wrong position
    # So each yellow hint is telling us to exclude from that position

    # Black/Wrong hint: Exclude from universal option
    # This is the same even for the case of this:
    # Correct answer is AAXYZ, we try X???X? - 1X will be yellow, other X will be wrong
    # For this case, we also need to exclude the position for yellow hint as well

    pass


def verify_hints(lines):
    # free positions -> will be removed by green hint
    # yellow hint positions
    # hint promotion from yellow to green - we can safely delete that yellow hint. We can just create another yellow hint for multi-letter case
    # Example: BBXYZ
    # ??B?? - B is yellow
    # ?B??? - B hint can be promoted to green(but we still need to remember 3 is the location to exclude)
    # ?B??B - 2nd B is yellow - we need to exclude B from position 2,3,5 (3 from previous record)

    # ---- Similar case but do both at the same time ---
    # ??B?? - B is yellow
    # ?B?B? - One B hint green and another B hint yellow

    pass

# 5 or less yellow hints?
# how to deal with duplicate yellow letters
# how to deal with hint promotion (yellow -> green -- still has a possibility of more of that letter)
# letter, possible_position

def show_permutation():
    pass

def main():
    hint = OverallHint()
    print(hint)

    #hint.wrong_letters.add("G")
    #hint.wrong_letters.add("A")
    hint.wrong_letters |= {"G", "A"}
    print(hint)

    should_try = ",".join(letters_to_try(hint))
    print(should_try)

    print("="*20)
    d,s = generate_round_counter_info("CREPE","WYYYG")
    print(d)
    print(s)


if __name__=="__main__":
    main()
