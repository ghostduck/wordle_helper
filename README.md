# The spoiler free Wordle helper module

Pure Python3 module to show Wordle hints without spoilers running on Python 3.11.

No list of words/dictionary is used. This module shows the correct patterns from the hints in guesses.

This helper module is very useful when you get several yellow letters.

The only external dependency is `pytest` for testing only.

---------------------------------------------

## Sample run on driver program (Console, Standard output)

You can just add more cases in `test_data.txt` to show the correct pattern and letters for blind guess of a Wordle game.

Each case is separated with a blank line.

Example:

```txt
# All empty lines and lines start with # are ignored.
# Empty line after a case indicate end of a set data.
PRIDE WYYWW
BIRTH WYYWW
INFRA YWYYY

PRIDE YYWWG
SPARE WYWYG
CREPE WYYYG
```

These are 2 sets of data of 2 Wordle games. Each of them has 3 guess.

Output of the sample driver program - Note that first few lines after each run are the colored output of the Wordle state (G/Y/W in background). The colour cannot be shown in this README file.

```txt
============== Run #1 ===========
PRIDE
BIRTH
INFRA
{'is_hard_mode_compatible': True,
 'is_normal_wordle_game': True,
 'is_super_hard_mode_compatible': True}
Letters for blind guess:
 Q W _ R _ Y U I O _
  A S _ F G _ J K L
    Z X C V _ _ M
Patterns for correct word:  ['RFAI*', 'RA*IF', 'R*AIF', 'RFA*I', 'RF*AI', 'RA*FI', 'R*AFI', 'FA*IR', 'F*AIR', 'AF*IR', '*FAIR']
============= End of Run #1 ============

============== Run #2 ===========
PRIDE
SPARE
CREPE
{'is_hard_mode_compatible': True,
 'is_normal_wordle_game': True,
 'is_super_hard_mode_compatible': False}
Letters for blind guess:
 Q W E R T Y U _ O P
  _ _ _ F G H J K L
    Z X _ V B N M
Patterns for correct word:  ['REP*E', 'R*PEE']
============= End of Run #2 ============
```

## Expected way to use the module

The smallest working example:

```python
from src.wordle_helper.wordle_no_spoiler_helper import process_all_hints

# outer level can be a list or tuple
in_data1 = (
    ("PRIDE","YYWWG"),
    ("SPARE","WYWYG"),
    ("CREPE","WYYYG"),
)
gen, _ = process_all_hints(in_data1, unknown_mark="*")
print("Patterns for correct word: ", [s for s in gen])

in_data2 = [
    ("PRIDE", "WYWWY"),
    ("MUTER", "YWWGG"),
    ("AMBER", "YYWGG"),
]
gen, _ = process_all_hints(in_data2, unknown_mark="*")
print("Patterns for correct word: ", [s for s in gen])
```

The output:

```txt
Patterns for correct word:  ['REP*E', 'R*PEE']
Patterns for correct word:  ['*AMER']
```

---------------------------------------------

## Run the test

We need to setup the environment to run the test first. Assume we use `venv`.

### Setup

```bash
# Setup venv
$ python3.11 -m  venv venv/wordle_m
$ source venv/wordle_m/bin/activate

$ python3 -m pip install --upgrade pip
$ pip install -U pytest

# Can just pip install after cloning this repo
$ pip install -r requirements.txt
```

### Reminder to me

The only dependency needed is `pytest` (7.2.0 at the moment I write these). I can fix the version and update `requirements.txt` this way.

```bash
$ pip freeze | tee requirements.txt
attrs==22.2.0
iniconfig==1.1.1
packaging==22.0
pluggy==1.0.0
pytest==7.2.0
```

### Really run the test

```bash
$ pytest  # at top level of directory

# or

$ python3 -m pytest

# Make print() shows up on the screen
# https://stackoverflow.com/questions/24617397/how-to-print-to-console-in-pytest
$ pytest --capture=no     # show print statements in console
$ pytest -s               # equivalent to previous command

$ pytest -v  # show more details on test
```

## Other information

I recommend telling git to ignore changes in `test_data.txt` as I find myself keep adding cases in the file when playing Wordles...

`git update-index --skip-worktree test_data.txt`
