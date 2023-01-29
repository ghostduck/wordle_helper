#!/usr/bin/python3


from collections import defaultdict

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
    # Guess  | BB???
    # Result | 1) YWWWW   2) YYWWW

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
            # setup data for yellow/wrong case
            correct_letter_count[correct_letter] += 1

            y_w_guess_indices.append(i)

    # Yellow/Wrong hints
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
