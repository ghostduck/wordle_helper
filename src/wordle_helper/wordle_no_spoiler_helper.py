#!/usr/bin/python3

WORDLE_LENGTH = 5
MAX_TRY = 6  # Not strictly enforced here
ALL_UPPER_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set, List
from itertools import combinations

@dataclass
class OverallHint:
    """Class for accumulated hints."""
    # list of correct letters and None
    # just treat this as the confimred (green) answers/letters of Wordle you can see on screen
    green_hints: list = field(default_factory=list)

    # yellow/wrong hint about the positions to exclude
    # dict of letter to set of int (positions to exclude)
    y_w_hint_excluded_position: Dict[str, Set[int]] = field(default_factory=defaultdict)

    # letters hinted for wrong guesses only (single letter W or multi-letter all W)
    # Just treat letters here have "A": (min: 0, max: 0)
    wrong_letters: Set[str] =  field(default_factory=set)
    # We will hint "correct letter but do not guess them anymore" (min_count == max_count) later

    # {"A": (min, max)} # min max is the letter count
    letter_min_max_counter: Dict[str, tuple[int, int]] = field(default_factory=defaultdict)

    def generate_combinations(self) -> List[tuple[str, List]]:
        """Return a List of tuples. Each tuple contains the letter and combinations of possible positions for yellow hints guess as a list. So the list does not contain green positions.

        Note that if there are multiple yellow hints of the same letter, the combinations of that letter can be returned too.

        For example: [
            ("E", [(2,3),(2,4),(3,4)])  # When we have to exclude 0,1 and there are 2 min_count for "E"
        ]

        """

        letter_min_count = {letter: min_count for letter, (min_count, _) in self.letter_min_max_counter.items()}
        green_positions_to_exclude = []

        # get count for letters for Y/W hints only
        for i, letter in enumerate(self.green_hints):
            if letter is not None:
                letter_min_count[letter] -= 1
                green_positions_to_exclude.append(i)

                if letter_min_count[letter] == 0:
                    del letter_min_count[letter]

        # combinations parts
        full_length = [i for i in range(len(self.green_hints)) if i not in green_positions_to_exclude]

        letter_combinations_lst = []

        for letter, letter_count in letter_min_count.items():
            positions_to_try = [i for i in full_length if i not in self.y_w_hint_excluded_position[letter]]
            comb = [c for c in combinations(positions_to_try, letter_count)]

            if len(comb) == 0:
                raise ValueError("Cannot generate valid combination for {}".format(letter))

            letter_combinations_lst.append((letter,comb))

        return letter_combinations_lst


def letters_to_try(hint) -> list:
    correct_letters_to_exclude = [letter.upper() for letter, (min_count, max_count) in hint.letter_min_max_counter.items() if min_count == max_count]

    return [l for l in ALL_UPPER_LETTERS if l not in hint.wrong_letters and l not in correct_letters_to_exclude]



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
    """Return a new dict of letter count based on input of guess and guess_result.

    This result includes green hints.
    """

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
    # (watch out for case like ???B?, XXBBX, WWWGW) [W first, G later for 'B']
    # for that letter - max = min (set upper limit)
    # Otherwise (wrong hint, single letter) - add to wrong letter

    letter_min_max_counters = dict()  # the min count includes green hints too
    wrong_letters = set()  # don't try these in blind guess

    # Green/Yellow hints
    letter_used = 0
    gy_gen = (i for i,r in enumerate(guess_result) if r == "G" or r == "Y")

    for i in gy_gen:
        guess_letter = guess[i]

        # counter logic
        if guess_letter not in letter_min_max_counters:
            # 3. create new entry

            # note that len(letter_min_max_counters) is wrong since possible to
            # have multiple "multiple letters" which leads to fewer entries in the dict
            # Like "CCDD" would only have 2 entries but already have 4 letters
            letter_min_max_counters[guess_letter] = (0, len(guess_result) - letter_used)

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

            # we will hint multiple letter guess with partial correct result later

        else:
            wrong_letters.add(guess_letter)

    return wrong_letters, letter_min_max_counters


def generate_round_position_exclusion_info(guess, guess_result):
    """Return a tuple consist of a list and a dictionary.

    The dictionary: y_w_hint_exclude
    - Indices: the letter of yellow hints
    - Value: Set of positions of integers to exclude (0-based)

    The list: current_confirmed_green
    - Simply a list of None or letters at the correct position

    """
    # assume already passed length check

    current_confirmed_green = [None] * len(guess_result)  # None means UNKNOWN
    y_w_hint_exclude = defaultdict(set)

    # green/yellow hints first
    for i, result in enumerate(guess_result):
        guess_letter = guess[i]

        if result == "G":
            current_confirmed_green[i] = guess_letter
        elif result == "Y":
            y_w_hint_exclude[guess_letter].add(i)

        # Do NOT handle Wrong hints here!

    # multiple letter wrong hint case
    w_gen = (i for i,r in enumerate(guess_result) if r == "W")
    for i in w_gen:
        guess_letter = guess[i]

        # Both Wrong and Yellow, Wrong and Green
        if (guess_letter in y_w_hint_exclude) or (guess_letter in current_confirmed_green):
            y_w_hint_exclude[guess_letter].add(i)

    return current_confirmed_green, y_w_hint_exclude


def random_thoughts():
    pass

    # how to handle invalid round-hint - like 4G1Y

    # multiple letter (considering all letters), Yellow -> Hint of minimum amount of letter, and multiple position to exclude
    # single letter, Yellow -> Hint of minimum amount of letter, and position to exclude
    # multiple letter (considering all letters), Wrong -> Tell us the maximum amount of letter, and multiple position to exclude, and should exclude from blind guess
    # single letter, Wrong -> Maximum amount of that letter is 0. Should exclude from blind guess

    # Green hint: Letter is in correct position
    # Need to remove from free positions

    # Yellow hint: Letter is in the word but wrong position
    # So each yellow hint is telling us to exclude from that position

    # Black/Wrong hint: Exclude from universal option
    # This is the same even for the case of this:
    # Correct answer is AAXYZ, we try X???X? - 1X will be yellow, other X will be wrong
    # For this case, we also need to exclude the position for yellow hint as well

    # hint promotion from yellow to green - we can safely delete that yellow hint. We can just create another yellow hint for multi-letter case

    # free positions -> will be removed by green hint
    # yellow hint positions
    # Example: BBXYZ, 3 rounds of input
    # ??B?? - B is yellow
    # ?B??? - B hint can be promoted to green(but we still need to remember 3 is the location to exclude)
    # ?B??B - 2nd B is yellow - we need to exclude B from position 2,3,5 (3 from previous records, 2 from green hint, 5 from yellow hint)

    # ---- Similar case but do both at the same time ---
    # ??B?? - B is yellow
    # ?B?B? - One B hint green and another B hint yellow

def validate_round_hint(round_hint):
    pass

def merge_hint(accumulated_hints, round_hint):
    for i, letter in enumerate(round_hint.green_hints):
        # Do nothing when round hint letter is None
        # Otherwise: if acc_hint_letter is None, overwrite it (as we find new letter)
        #          - if acc_hint_letter is not None and different from current letter, raise error (inconsistent green hint)
        acc_hint_letter = accumulated_hints.green_hints[i]
        if letter is not None and acc_hint_letter != letter:
            if acc_hint_letter is not None:
                raise ValueError("Inconsistent green hint: current round letter {}, current accumulated hint {}, current index {}".format(letter, accumulated_hints.green_hints[i], i))
            else:
                # cover case of acc.green_hint[i] is None (find new letter)
                accumulated_hints.green_hints[i] = letter

    # no validation, just add
    # error will be checked when the combination is created
    for letter, s in round_hint.y_w_hint_excluded_position.items():
        accumulated_hints.y_w_hint_excluded_position[letter] |= s

    # just add, again...
    accumulated_hints.wrong_letters |= round_hint.wrong_letters

    # just use stricter min/max count
    for letter, (min_count, max_count) in round_hint.letter_min_max_counter.items():
        if letter not in accumulated_hints.letter_min_max_counter:
            accumulated_hints.letter_min_max_counter[letter] = (min_count, max_count)
        else:
            new_min_count = max(accumulated_hints.letter_min_max_counter[letter][0], min_count)
            new_max_count = min(accumulated_hints.letter_min_max_counter[letter][1], max_count)

            accumulated_hints.letter_min_max_counter[letter] = (new_min_count, new_max_count)


def generate_round_data(guess, guess_result):
    green_hints, y_w_hint_excluded_position = generate_round_position_exclusion_info(guess, guess_result)

    wrong_letters, letter_min_max_counter = generate_round_counter_info(guess, guess_result)

    return green_hints, y_w_hint_excluded_position, wrong_letters, letter_min_max_counter

def process_all_hints(hints:List[tuple[str,str]]):
    """The main part of the module. Return the generator with additional data of the Wordle guesses.

    Input: List of tuples.
    Each tuple has 2 strings - first is letter gussed and second is the result (Y/G/W)

    Output: ?????

    """
    accumulated_hints = None

    for h in hints:
        verify_hints(*h)

        data = generate_round_data(*h)
        o_h = OverallHint(*data) # do not forget the * to unpack tuple

        validate_round_hint(o_h)
        if accumulated_hints is None:  # for first round hint
            accumulated_hints = o_h
        else:
            merge_hint(accumulated_hints, o_h)


    comb = accumulated_hints.generate_combinations()
    print(comb)

    return hints


def add_round_hints():
    pass


def basic_hint_check(guess, guess_result):
    if len(guess) != len(guess_result):
        raise ValueError("guess and guess_result have different length.")

    if len(guess) <= 0:
        raise ValueError("Invalid guess length: must be greater than 0")

    valid_result = all(r in "GYW" for r in guess_result)
    if not valid_result:
        raise ValueError("Something not G/Y/W inside the guess_result string: {}".format(guess_result))

    return True

def verify_hints(guess, guess_result):
    """Return True if the single round hint is valid on its own. Otherwise raise Exception.

    Valid means "nothing contradictory".Some invalid inputs are like 4G1Y, 3Y on same letter (when Wordle size is 5)

    Note that a valid round hint can still be contradictory to accumulated hints.

    """

    basic_hint_check(guess, guess_result)  # length and WGY only

    # Then check the logic



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
