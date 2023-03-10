#!/usr/bin/python3

WORDLE_LENGTH = 5
MAX_TRY = 6  # Not strictly enforced here
ALL_UPPER_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
UNKNOWN_MARK = "?"

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
    # dict of letter to set of int (positions to exclude, 0-based)
    y_w_hint_excluded_position: Dict[str, Set[int]] = field(default_factory=dict)

    # letters hinted for wrong guesses only (single letter W or multi-letter all W)
    # Just treat letters here have "A": (min: 0, max: 0)
    wrong_letters: Set[str] =  field(default_factory=set)
    # We will hint "correct letter but do not guess them anymore" (min_count == max_count) later

    # {"A": (min, max)} # min max is the letter count
    letter_min_max_counter: Dict[str, tuple[int, int]] = field(default_factory=dict)

    def generate_combinations(self) -> Dict[str, List[tuple[int]]]:
        """Return a dict of letter to List. Each list contains combinations of possible positions (as a tuple of int) for yellow hints guess. It does not contain green positions.

        Note that if there are multiple yellow hints of the same letter (min_count >1), the combinations of that letter can be returned too.

        For example: {
            "A" -> [(2,),(4,)],  # 1 min_count for A, exclude 0,1,3
            "E" -> [(2,3),(2,4),(3,4)]  # When we have to exclude 0,1 and there are 2 min_count for "E"
        }

        """

        letter_min_count = {letter: min_count for letter, (min_count, _) in self.letter_min_max_counter.items()}
        green_positions_to_exclude = []

        # Setup: Exclude green hints to get count for letters for Y/W hints
        for i, letter in enumerate(self.green_hints):
            if letter is not None:
                letter_min_count[letter] -= 1
                green_positions_to_exclude.append(i)

                # This local counter contains both G and Y hints, remove G hints
                # so the counter will be for Y hints only
                if letter_min_count[letter] == 0:
                    del letter_min_count[letter]

        # combinations parts (Yellow hints)
        # For individual letter exclusion, exclude green hint
        # and then its yellow hints exclusion
        # (Full - green - yw_hints[letter])
        full_length = [i for i in range(len(self.green_hints)) if i not in green_positions_to_exclude]

        letter_combinations_dict = dict()

        for letter, letter_count in letter_min_count.items():
            positions_to_try = [i for i in full_length if i not in self.y_w_hint_excluded_position[letter]]
            comb = [c for c in combinations(positions_to_try, letter_count)]

            # Many invalid cases can be caught here when too many positions are excluded
            if len(comb) == 0:
                raise ValueError("Cannot generate valid combination for letter {}".format(letter))

            letter_combinations_dict[letter] = comb

        return letter_combinations_dict


    # About generator hinting
    # https://stackoverflow.com/questions/57363181/proper-use-generator-typing
    def correct_pattern_gen(self, unknown_mark:str=UNKNOWN_MARK) -> Generator[str, None, None]:
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
            # pattern is one of the Cartesian product of all the possible
            # positions of all the yellow/wrong hint letters
            # pattern = ((1,), (2,), (3,4,),)

            # put all the ints inside tuples together as a list, flatten using chain
            flattened_list = [i for i in chain.from_iterable(pattern)]

            # Check all indices are unique or not by converting to set
            if len(flattened_list) == len(set(flattened_list)):
                pattern_count += 1

                # Build the string - deepcopy from green hint, replace None with UNKNOWN_MARK
                str_builder = self.str_builder_for_output(unknown_mark)

                # Fill in string builder - combs.keys() and values() have same order
                for i, pos in enumerate(pattern):
                    letter = lst_of_letters[i]
                    for p in pos:
                        str_builder[p] = letter

                yield "".join(str_builder)

        # Still need to return a pattern even when there are no yellow hints
        if pattern_count == 0:
            yield "".join(self.str_builder_for_output(unknown_mark))


    def str_builder_for_output(self, unknown_mark:str=UNKNOWN_MARK) -> List[str]:
        """Return a List to be used in str.join() showing the state of green hint letters.

        We just deepcopy from green_hint and replace None with UNKNOWN_MARK.
        """
        return [l if l is not None else unknown_mark for l in self.green_hints[:]]


    def letters_for_unknown_guess(self) ->List[str]:
        #  the multiple case letters with G/W or Y/W hints
        correct_letters_to_exclude = [letter.upper() for letter, (min_count, max_count) in self.letter_min_max_counter.items() if min_count == max_count]

        # =(ALL_UPPER_LETTERS - correct_letters that should not try - wrong letters)
        return [l for l in ALL_UPPER_LETTERS if l not in self.wrong_letters and l not in correct_letters_to_exclude]


def generate_round_counter_info(guess:str, guess_result:str):
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
    # known_max_length is only 5 for standard Wordle

    #(min/current, max) -> default (1, known_max_length)

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
    # - 3. otherwise - create entry for current letter, (1, MAX - number of letters used)

    # !!! New wrong hint (multiple letter) - must be processed after B/G hint !!!
    # (watch out for case like ???B?, XXBBX, WWWGW) [W first, G later for 'B']
    # for that letter (B in example) - max = min (set upper limit)
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
            # Multiple letter case: Y/W or G/W together
            cur_count, _ = letter_min_max_counters[guess_letter]
            letter_min_max_counters[guess_letter] = (cur_count, cur_count)  # reduce max length to min/current length

            # Exclusion of wrong positions in multiple letter guess case will be handled in generate_round_position_exclusion_info()
        else:
            # Single letter wrong hint goes here
            wrong_letters.add(guess_letter)

    return wrong_letters, letter_min_max_counters


def generate_round_position_exclusion_info(guess:str, guess_result:str):
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


def cross_check_wrong_hints(hint1:OverallHint, hint2:OverallHint):
    """Raise if hint1's green/yellow hint letters are in hint2's wrong letter set.

    This check is useful when they are both refering to the same correct answer.

    Note that for all letters, it can be either part of the correct answer (G/Y) or not part of answer (W).
    So if any letters are found in both part, there must be an error.
    """

    for letter in hint2.wrong_letters:
        if letter in hint1.y_w_hint_excluded_position or letter in hint1.green_hints:
            raise ValueError("Letter {} failed wrong hint cross check".format(letter))


def verify_contradiction(accumulated_hints_before_merge:OverallHint, round_hint:OverallHint):
    """Raise if contradiction of 2 hints are found.

    Both hint are expected to refer to the same correct word.

    We assume the accumulated_hints have the correct information.
    """
    for i, (acc_hint_letter, round_hint_letter) in enumerate(zip(accumulated_hints_before_merge.green_hints, round_hint.green_hints, strict=True)):

        # For both accumulated and round hint, nothing to verify if we don't know the correct letter for this position
        if acc_hint_letter is not None:
            # G -> Y (same position)
            # Use dict.get() to return empty list for non-existing key so that part is False
            if i in round_hint.y_w_hint_excluded_position.get(acc_hint_letter, []):
                raise ValueError("Current yellow hint excludes position {} for letter {} but it was green before".format(i, acc_hint_letter))

        if round_hint_letter is not None:
            # Y -> G (same position)
            # Note: DON'T use y_w_hint_excluded_position[letter] as it will create empty set in real dict
            if i in accumulated_hints_before_merge.y_w_hint_excluded_position.get(round_hint_letter, set()):
                raise ValueError("Current round is green hint for letter {} at position {} but it was excluded before in yellow/wrong hint".format(round_hint_letter, i))

        if round_hint_letter is not None and \
        acc_hint_letter is not None and \
        acc_hint_letter != round_hint_letter:
            # G -> G (Same position, different letter)
            raise ValueError("Inconsistent green hint: current round letter {}, current accumulated hint {}, current index {}".format(round_hint_letter, accumulated_hints_before_merge.green_hints[i], i))

    # G/Y -> W
    cross_check_wrong_hints(accumulated_hints_before_merge, round_hint)
    # W -> G/Y
    cross_check_wrong_hints(round_hint, accumulated_hints_before_merge)

    # Check length
    for letter, (min_len, _) in round_hint.letter_min_max_counter.items():
        if letter in accumulated_hints_before_merge.letter_min_max_counter:
            acc_min, acc_max = accumulated_hints_before_merge.letter_min_max_counter[letter]
            # Note: [range(1,1)] gives empty list, so don't forget +1 on max
            if min_len not in range(acc_min, acc_max+1):
                raise ValueError("Number of letters of {} is contradictory to accumulated hint - must be between {} to {}. Current length is {}".format(letter, acc_min, acc_max, min_len))


def validate_round_hint(round_hint:OverallHint):
    # Exception will be raised if combination cannot be generated
    round_hint.generate_combinations()

    # check number of letters for correct guesses (G/Y)
    hint_min_sum = sum([v[0] for v in round_hint.letter_min_max_counter.values()])
    if len(round_hint.green_hints) < hint_min_sum:
        raise ValueError("More correct letters than length of correct word")


def merge_hint(accumulated_hints:OverallHint, round_hint:OverallHint):
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
            acc_min, acc_max = accumulated_hints.letter_min_max_counter[letter]
            new_min_count = max(acc_min, min_count)
            new_max_count = min(acc_max, max_count)

            accumulated_hints.letter_min_max_counter[letter] = (new_min_count, new_max_count)


def generate_round_data(guess:str, guess_result:str):
    green_hints, y_w_hint_excluded_position = generate_round_position_exclusion_info(guess, guess_result)

    wrong_letters, letter_min_max_counter = generate_round_counter_info(guess, guess_result)

    return green_hints, y_w_hint_excluded_position, wrong_letters, letter_min_max_counter


def check_hint_is_hard_compatible(accumulated_hints_before_merge:OverallHint, round_hint:OverallHint):
    """Return True if:
    1) all green hints in accumulated_hints are used and
    2) all yellow hints in accumulated_hints are used. These hints end up as green or yellow hint in round hint.

    Otherwise return False

    The checking of 2) will be done using letter_min_max_counter.
    """

    # First check all green hints in accumulated_hints are followed or not
    for acc_hint_letter, round_hint_letter in zip(accumulated_hints_before_merge.green_hints, round_hint.green_hints, strict=True):
        if acc_hint_letter is not None and round_hint_letter != acc_hint_letter:
            return False

    # Then check all yellow hints in accumulated_hints are used or not
    for letter in accumulated_hints_before_merge.y_w_hint_excluded_position:
        # prevent raising KeyNotFound - get 0 instead for this case
        current_hint_letter_count = round_hint.letter_min_max_counter.get(letter,(0,0))[0]

        acc_min, _ =  accumulated_hints_before_merge.letter_min_max_counter[letter]

        # it is a valid hard mode as long as the accumulated min count is followed
        if not current_hint_letter_count >= acc_min:
            return False

    return True

def check_hint_is_super_hard_compatible(accumulated_hints_before_merge:OverallHint, round_hint:OverallHint):
    """Return True if round hint is a valid for "super hard" mode or not.

    Super hard mode is not defined in normal Wordle. Some other variants implemented that.
    It means "totally no waste" by matching these conditions:
    0) Must be in hard mode
    1) Confirmed Wrong hints cannot be used at future guesses
    2) Yellow/Wrong hints excluded positions cannot be used for that letter
    3) Green/Wrong or Yellow/Wrong hints shows the upper limit of that letter and this must be followed

    This function only checks 1 to 3.

    In other words, "super hard" mode means only guessing the correct pattern from correct_pattern_gen() and strictly use letters from letters_for_unknown_guess()
    """

    # 1) Simply set intersection
    if round_hint.wrong_letters & accumulated_hints_before_merge.wrong_letters:
            return False

    # 2) Also set intersection but need to handle key not found
    for letter, pos in round_hint.y_w_hint_excluded_position.items():
        acc_pos = accumulated_hints_before_merge.y_w_hint_excluded_position.get(letter, set())
        if acc_pos & pos:
            return False

    # 3) Check length and use the upper limit
    # Mostly copy from check_hint_is_hard_compatible()
    for letter in accumulated_hints_before_merge.y_w_hint_excluded_position:
        current_hint_letter_count = round_hint.letter_min_max_counter.get(letter,(0,0))[0]
        acc_min, acc_max =  accumulated_hints_before_merge.letter_min_max_counter[letter]
        if current_hint_letter_count not in range(acc_min, acc_max+1):
            return False

    return True


def process_all_hints(hints:List[tuple[str,str]], unknown_mark:str=UNKNOWN_MARK):
    """The main part of the module. Return the generator with additional data of the Wordle guesses.

    Input: List of tuples. (Tuple of tuples are OK too)
    Each tuple has 2 strings - first is letter gussed and second is the result (Y/G/W)

    (Optional parameter: Display letter for unknown characters will be change to this. Personally recommend one of these: */?/_)

    Output: Generator of correct patterns (as strings) and dictionary of additional information.

    """
    accumulated_hints = None
    is_hard_mode_compatible = True
    is_super_hard_mode_compatible = True

    # Can add more features here

    for h in hints:
        verify_hints(*h)

        data = generate_round_data(*h)
        current_hints = OverallHint(*data) # do not forget the * to unpack tuple

        validate_round_hint(current_hints)
        if accumulated_hints is None:  # for first round hint
            accumulated_hints = current_hints
        else:
            verify_contradiction(accumulated_hints, current_hints)

            # for additional info only
            # Check round hints before merge
            if is_hard_mode_compatible:
                is_hard_mode_compatible = check_hint_is_hard_compatible(accumulated_hints, current_hints)

            if is_super_hard_mode_compatible:
                is_super_hard_mode_compatible = is_hard_mode_compatible and check_hint_is_super_hard_compatible(accumulated_hints, current_hints)

            merge_hint(accumulated_hints, current_hints)
            validate_round_hint(accumulated_hints)

    # All hints are processed
    patterns = accumulated_hints.correct_pattern_gen(unknown_mark)
    # Can add read a dictionary with spoiler here then filter out the words here
    # But I am not going to do that as this is no spoiler hint provider

    # for additional info only
    additional_info = dict()
    additional_info["letters_for_unknown_guess"] = accumulated_hints.letters_for_unknown_guess()
    additional_info["is_hard_mode_compatible"] = is_hard_mode_compatible
    additional_info["is_super_hard_mode_compatible"] = is_super_hard_mode_compatible
    # Can add checking like no more entries after GGGGG but I don't bother it for now
    additional_info["is_normal_wordle_game"] = len(accumulated_hints.green_hints) == WORDLE_LENGTH and len(hints) <= MAX_TRY

    return patterns, additional_info



def verify_hints(guess:str, guess_result:str):
    """Raise Exception if the guess or guess_result (G/Y/W) is invalid.

    Note that a valid round hint can still be contradictory to accumulated hints.
    Further checking like 4G1Y, 3Y on same letter will be done in validate_round_hint()
    """

    if len(guess) != len(guess_result):
        raise ValueError("guess and guess_result have different length.")

    if len(guess) <= 0:
        raise ValueError("Invalid guess length: must be greater than 0")

    valid_result = all(r in "GYW" for r in guess_result)
    if not valid_result:
        raise ValueError("Something not G/Y/W inside the guess_result string: {}".format(guess_result))
