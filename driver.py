from src.wordle_helper.console_print_helper import console_wordle_printline

def main():
    test_input = [
        ("PRIDE", "YYWWG"),
        ("SPARE", "WYWYG"),
        ("CREPE", "WYYYG"),
        ("RUPEE", "GGGGG")
    ]

    for word, color in test_input:
        console_wordle_printline(word, color)


if __name__=="__main__":
    main()
