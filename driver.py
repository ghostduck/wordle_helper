from src.wordle_helper.console_print_helper import console_wordle_printline
from src.wordle_helper.wordle_no_spoiler_helper import process_all_hints

def read_cases_with_answers_from_file(path):
    list_of_guesses = []

    with open(path) as file:
        for line in file:
            line = line.strip()

            # skip comment line and blank line
            if (bool(line) and not line.startswith("#")):
                guess, result = line.split(" ")
                list_of_guesses.append((guess, result))

    return list_of_guesses

def main():
    test_input = [
        ("PRIDE", "YYWWG"),
        ("SPARE", "WYWYG"),
        ("CREPE", "WYYYG"),
        ("RUPEE", "GGGGG")
    ]

    for word, color in test_input:
        console_wordle_printline(word, color)

    lst = read_cases_with_answers_from_file("test_data.txt")
    gen = process_all_hints(lst)

    print("gachiBASS")
    print("Patterns for correct word: ", [s for s in gen])
    print("done")


if __name__=="__main__":
    main()
