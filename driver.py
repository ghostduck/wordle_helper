from src.wordle_helper.console_print_helper import console_wordle_printline, print_capital_letters_like_keyboard_layout
from src.wordle_helper.wordle_no_spoiler_helper import process_all_hints
from pprint import pprint

def test_console_wordle_printline():
    test_input = [
        ("PRIDE", "YYWWG"),
        ("SPARE", "WYWYG"),
        ("CREPE", "WYYYG"),
        ("RUPEE", "GGGGG")
    ]

    print("Start printing test")
    for word, color in test_input:
        console_wordle_printline(word, color)
    print("End printing test")


# copy same "reading file to list" code from testing code
def read_cases_with_answers_from_file(path):
    list_of_cases = []
    guesses = ()

    # Each case is a tuple of many guesses.
    # The tuple is like a list. It contains many pairs of guessed word and results

    # Example of an item:
    # list_of_cases[0] = (
    #    ("PRIDE", "YYWWG"),
    #    ("SPARE", "WYWYG"),
    #    ...
    # )

    with open(path) as file:
        for line in file:

            line = line.strip()

            # skip comment line
            if not line.startswith("#"):

                # blank line
                if not bool(line):
                    # some valid cases before
                    if bool(guesses):
                        # add existing valid cases, then clean everything up for new case
                        list_of_cases.append(guesses)
                        guesses = ()  # just like guesses.clear() but it is a tuple
                else:
                    # assume to be guesses line
                    guess_word, outcome = line.split()
                    if not (len(guess_word) == len(outcome)):
                        raise ValueError("guess_word and outcome not having same length. {} - {}".format(guess_word, outcome))
                    guesses += ((guess_word, outcome),)

    # Finish reading file (End of file)
    # Too bad I have to repeat myself ...
    if bool(guesses):
        list_of_cases.append(guesses)

    return list_of_cases

def console_process_hint(hint):
    for word, color in hint:
        console_wordle_printline(word, color)

    gen, extra_info = process_all_hints(hint, unknown_mark="*")

    letters_for_unknown_guess = extra_info.pop("letters_for_unknown_guess")
    pprint(extra_info)
    print("Letters for blind guess:")
    print_capital_letters_like_keyboard_layout(letters_for_unknown_guess)
    print("Patterns for correct word: ", [s for s in gen])

def main():
    # test_console_wordle_printline()

    lst = read_cases_with_answers_from_file("test_data.txt")

    for i, hint in enumerate(lst):
        print("============== Run #{} ===========".format(i))
        console_process_hint(hint)
        print("============= End of Run #{} ============\n".format(i))

if __name__=="__main__":
    main()
