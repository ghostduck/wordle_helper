#!/usr/bin/python3

WORDLE_LENGTH = 5
MAX_TRY = 6  # Not strictly enforced here
ALL_UPPER_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
UNKNOWN_MARK = "?"

# TODO: about W error cases: change way to check counter - don't want multiple if checking on green and yellow hint

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set, List, Generator
from itertools import combinations, product, chain

@dataclass
class OverallHint:
    """Class for accumulated hints."""
    # list of correct letters and None
    # just treat this as the confirmed (green) answers/letters of Wordle you can see on screen
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

    def generate_combinations(self) -> Dict[str, List[tuple[int]]]:
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
        # For individual letter exclusion, we have to exclude green hint and its yellow hints exclusion (Full - green - yw_hints[letter])
        full_length = [i for i in range(len(self.green_hints)) if i not in green_positions_to_exclude]

        letter_combinations_dict = dict()

        for letter, letter_count in letter_min_count.items():
            positions_to_try = [i for i in full_length if i not in self.y_w_hint_excluded_position[letter]]
            comb = [c for c in combinations(positions_to_try, letter_count)]

            if len(comb) == 0:
                raise ValueError("Cannot generate valid combination for {}".format(letter))

            letter_combinations_dict[letter] = comb

        return letter_combinations_dict

    # About generator hinting
    # https://stackoverflow.com/questions/57363181/proper-use-generator-typing
    def correct_pattern_gen(self) -> Generator[str, None, None]:
        """The generator function which returns the correct patterns as string."""

        # The idea: Simple looping + exclude same location seems to be the best
        combs = self.generate_combinations()
        # print("Combs is like: ", combs)

        pattern_count = 0
        lst_of_letters = list(combs.keys())
        lst_of_pos = combs.values()

        # Reminder: Each small list contains tuples
        # Each tuple may have more than multiple indicies and pattern is a tuple
        for pattern in product(*lst_of_pos):
            flattened_list = [i for i in chain.from_iterable(pattern)]
            # TODO: Test multiple letter case !!!!!!
            # Check all indices are unique or not by converting to set
            if len(flattened_list) == len(set(flattened_list)):
                pattern_count += 1

                # Build the string - deepcopy from green hint, replace None with UNKNOWN_MARK
                str_builder = self.str_builder_for_output()

                # Fill in string builder - combs.keys() and values() have same order
                for i, pos in enumerate(pattern):
                    letter = lst_of_letters[i]
                    for p in pos:
                        str_builder[p] = letter

                yield "".join(str_builder)

        # Still need to return a pattern even when there are no yellow hints
        if pattern_count == 0:
            yield "".join(self.str_builder_for_output())


    def str_builder_for_output(self) -> List[str]:
        """Return a List to be used in str.join() showing the state of green hint letters.

        We just deepcopy from green_hint and replace None with UNKNOWN_MARK.
        """
        return [l if l is not None else UNKNOWN_MARK for l in self.green_hints[:]]

    def letters_for_unknown_guess(self) ->List[str]:
        correct_letters_to_exclude = [letter.upper() for letter, (min_count, max_count) in self.letter_min_max_counter.items() if min_count == max_count]

        return [l for l in ALL_UPPER_LETTERS if l not in self.wrong_letters and l not in correct_letters_to_exclude]


def generate_round_counter_info(guess, guess_result):
    """Return a set and a new dict.

    Set: set of wrong letters.

    Letter in this set strictly means min_count: 0 and max_count: 0.
    So letters appear in this set should not appear in green hints and y_w_hint_exclude at all.

    Dict: Letter count based on input of guess and guess_result.
    Key: Letter
    Value: Tuple of 2 integers.

    Example: {"K": (1,3)}. This means K has min_count of 1 and max_count of 3 in correct guess.

    This count dict includes green hints.
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
            # Multiple letter case: Y/G and W together
            cur_count, _ = letter_min_max_counters[guess_letter]
            letter_min_max_counters[guess_letter] = (cur_count, cur_count)  # reduce max length to min/current length

            # Exclusion of wrong positions in multiple letter guess case will be handled in generate_round_position_exclusion_info()
        else:
            # Single letter wrong hint goes here
            wrong_letters.add(guess_letter)

    return wrong_letters, letter_min_max_counters


def generate_round_position_exclusion_info(guess, guess_result):
    """Return a tuple consist of a list and a dictionary.

    The dictionary: y_w_hint_exclude
    - Indices: the letter of yellow hints
    - Value: Set of positions of integers to exclude (0-based). This set checks the position of Wrong letters in multiple letter case

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


def verify_contradiction(accumulated_hints, round_hint):
    for i, letter in enumerate(round_hint.green_hints):

        acc_hint_letter = accumulated_hints.green_hints[i]
        if acc_hint_letter is not None:
            # Contradiction check: G -> Y
            # Use dict.get() to return empty list for non-existing key so that part is False
            if i in round_hint.y_w_hint_excluded_position.get(acc_hint_letter, []):
                raise ValueError("Current yellow hint excludes position {} for letter {} but it was green before".format(i, acc_hint_letter))

            # Contradiction check: G -> W
            if acc_hint_letter in round_hint.wrong_letters:
                raise ValueError("Current wrong hint excludes letter {} but it was green before".format(acc_hint_letter))

        if letter is not None and acc_hint_letter != letter:
            # Contradiction check: Y -> G
            if i in accumulated_hints.y_w_hint_excluded_position[letter]:
                raise ValueError("Current round is green hint for letter {} at position {} but it was excluded before in yellow/wrong hint".format(letter, i))

            # Contradiction check: W -> G
            if letter in accumulated_hints.wrong_letters:
                raise ValueError("Current round is green hint for letter {} at position {} but it was excluded before in wrong hint".format(letter, i))

            if acc_hint_letter is not None:
                # Same green position but different letter: G -> G (different letter)
                raise ValueError("Inconsistent green hint: current round letter {}, current accumulated hint {}, current index {}".format(letter, accumulated_hints.green_hints[i], i))

    for letter, s in round_hint.y_w_hint_excluded_position.items():
        # Contradiction check: W -> Y
        if letter in accumulated_hints.wrong_letters:
            raise ValueError("Previously excluded wrong letter {} is now included in yellow hint.".format(letter))

    # Contradiction check: Y -> W
    for letter in round_hint.wrong_letters:
        if letter in accumulated_hints.y_w_hint_excluded_position:
            raise ValueError("Previously yellow hint letter {} is now included as wrong letter".format(letter))


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
    # Exception will be raised if combination cannot be generated
    round_hint.generate_combinations()

def merge_hint(accumulated_hints, round_hint):
    # Assume no contradictions since already checked in other functions
    for i, letter in enumerate(round_hint.green_hints):

        acc_hint_letter = accumulated_hints.green_hints[i]

        if acc_hint_letter is None:
            # find new letter (None -> New letter), or just (None -> None)
            accumulated_hints.green_hints[i] = letter

    for letter, s in round_hint.y_w_hint_excluded_position.items():
        # No special logic to check
        accumulated_hints.y_w_hint_excluded_position[letter] |= s

    # No special check too
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
    # TODO: Add additional info
    accumulated_hints = None

    for h in hints:
        verify_hints(*h)

        data = generate_round_data(*h)
        o_h = OverallHint(*data) # do not forget the * to unpack tuple

        validate_round_hint(o_h)
        if accumulated_hints is None:  # for first round hint
            accumulated_hints = o_h
        else:
            verify_contradiction(accumulated_hints, o_h)
            merge_hint(accumulated_hints, o_h)

    # TODO: move this to additional info
    print("Letters for blind guess: ", "".join(accumulated_hints.letters_for_unknown_guess()))
    patterns = accumulated_hints.correct_pattern_gen()
    return patterns


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

    #should_try = ",".join(letters_to_try(hint))
    #print(should_try)

    print("="*20)
    d,s = generate_round_counter_info("CREPE","WYYYG")
    print(d)
    print(s)


if __name__=="__main__":
    main()
