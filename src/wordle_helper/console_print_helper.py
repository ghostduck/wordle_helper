#!/usr/bin/python3

import curses

def choose_colour_str_method():
    """Choose colour string method according to terminal colour support.
    Only 256 or 16 colour support is expected.

    Output: colored_256_str or colored_16_str function.
    """
    # Reference:
    # https://codeyarns.com/tech/2015-03-18-how-to-check-colors-supported-by-terminal.html
    # https://github.com/l0b0/xterm-color-count
    # Note: Checking the value of $TERM seems not very reliable

    # https://stackoverflow.com/a/8496106
    # Seems using curses is the best

    curses.setupterm()
    supported_value = curses.tigetnum("colors")  # return 256 is console support 256 bit output

    if supported_value == 256:
        return colored_256_str
    elif supported_value == 16:
        return colored_16_str
    else:
        raise ValueError("Unexpected supported console color printing value: {}".format(supported_value))


def colored_256_str(text, bg_color):
    """Parse a string and 1 background color indictaor ("G"/"Y"/"W").

    Return the background'coloured with white letter string.
    Expect this function to be called when console supports 256 colours output.
    """

    # From https://stackabuse.com/how-to-print-colored-text-in-python/

    # Scheme:
    # For xterm-256color (Run echo $TERM # in your console)

    # ESCAPE CODE[ : \033[
    # BG_FG : 48 or 38 # 48 for Background color, 38 for Foreground / text color
    # SEPARATOR : ;5; # hardcoded?
    # COLOR_CODE : 0-255
    # STOPPER : m

    ESACPE_CODE = "\033["
    IS_BG_COLOR = "48"
    IS_TEXT_COLOR = "38"
    BG_COLOR = ""
    TEXT_COLOR = "255"  # always white in our wordle case, can choose something darker (like 250)
    SEPARATOR = ";5;"
    STOPPER = "m"

    if bg_color == "G":
        BG_COLOR = "28"
    elif bg_color == "Y":
        BG_COLOR = "94"
    elif bg_color == "W":
        BG_COLOR = "237"  # Grey or black
    else:
        raise ValueError("Unexpected color pattern input: {}".format(bg_color))

    bg_str = ESACPE_CODE + IS_BG_COLOR + SEPARATOR + BG_COLOR + STOPPER
    text_color_str = ESACPE_CODE + IS_TEXT_COLOR + SEPARATOR + TEXT_COLOR + STOPPER

    # closer - indicate terminal to go back to normal state, same as "\033[0;0m"
    COLOR_CLOSER = ESACPE_CODE + "0;0" + STOPPER

    color_str = bg_str + text_color_str + text + COLOR_CLOSER
    return color_str

def colored_16_str(text, bg_color):
    """Parse a string and 1 background color indictaor ("G"/"Y"/"W").

    Return the background'coloured with white letter string.
    Expect this function to be called when console supports 16 colours output.
    """

    # Note: The 16/8 bit output is really ugly in console ...

    ESACPE_CODE = "\033["
    STYLE = "0"  # Assume no style
    # Don't know why cannot show white color in Visual Studio Code's console below. But the code is correct
    TEXT_COLOR_WITH_SEPERATOR = ";37;"  # Always white
    BG_COLOR = ""  # To be filled in
    STOPPER = "m"

    # 8 bit output really hurt my eyes ...
    if bg_color == "G":
        BG_COLOR = "42"
    elif bg_color == "Y":
        BG_COLOR = "43"
    elif bg_color == "W":
        BG_COLOR = "40"
    else:
        raise ValueError("Unexpected color pattern input: {}".format(bg_color))

    COLOR_CLOSER = ESACPE_CODE + "0;0" + STOPPER

    color_str = ESACPE_CODE + STYLE + TEXT_COLOR_WITH_SEPERATOR + BG_COLOR + STOPPER + text + COLOR_CLOSER
    return color_str


def console_wordle_printline(word, wordle_bg):
    if len(word) != len(wordle_bg):
        raise("Word and background string has different length")

    color_output_fn = choose_colour_str_method()

    output = ""
    for letter, bg_color in zip(word, wordle_bg):
        output += color_output_fn(letter, bg_color)

    print(output)


def print_capital_letters_like_keyboard_layout(letters_to_print:str, hidden_letter_display:str="_", space_separate_length:int=1):
    """Print letters_to_print in a keyboard-like output to standard output.

    Can customize the hidden_letter_display and space length for letter separation.

    Example: letters_to_print="CQS" (hidden_letter_display="_", space_separate_length=1)

    Then we print:
    Q _ _ _ _ _ _ _ _ _ _
     _ S _ _ _ _ _ _ _
      _ _ C _ _ _ _

    """

    letters_to_print = letters_to_print.upper()
    keyboard_layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]  # length: 10,9,7
    keyboard_layout_length = [len(k_l) for k_l in keyboard_layout]

    separator = " " * space_separate_length

    # Display length calculation:
    # 1 space before the first letter, 1 space after the last letter
    # Longest row has n letters, we will need n-1 spaces to separate them
    # So the display length will be [2 + ((max_row_length -1) * space_separate_length) + max_row_length ]
    display_length = (max(keyboard_layout_length)-1) * space_separate_length + max(keyboard_layout_length) + 2

    for k_l in keyboard_layout:
        letters_to_display =  [l if l in letters_to_print else hidden_letter_display for l in k_l ]

        out = separator.join(letters_to_display)
        print(out.center(display_length))
