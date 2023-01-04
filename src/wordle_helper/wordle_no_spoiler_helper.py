#!/usr/bin/python3

WORDLE_LENGTH = 5
MAX_TRY = 6  # Not strictly enforced here


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
    correct_letter_count = {}
    y_w_guess_indices = []

    # Handle green hints first
    for i, guess_letter in enumerate(guess):
        correct_letter = answer[i]
        if guess_letter == correct_letter:
            output[i] = "G"
        else:
            # setup data for yellow / wrong case
            if correct_letter not in correct_letter_count:
                correct_letter_count[correct_letter] = 1
            else:
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



def parse_single_round_hint(guess, guess_result):
    # assume already passed length check

    current_confirmed_green = [None] * len(guess_result)  # None means UNKNOWN

    # green hints first
    for i, r in enumerate(guess_result):
        if r == "G":
            current_confirmed_green[i] = guess[i]

        # After excluding green hints in free position
        # multiple letter, Yellow -> Hint of minimum amount of letter, and multiple position to exclude
        # single letter, Yellow -> Hint of minimum amount of letter, and position to exclude
        # multiple letter, Wrong -> Tell us the maximum amount of letter, and multiple position to exclude, and should exclude from blind guess
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
