# The module

Pure Python3 module to show Wordle hints without spoilers.

No list of words are used. Only show the pattern from the hints from guesses.

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

# But I guess I can ignore everything other than pytest, so I remove everything else
$ cat requirements.txt
pytest==7.2.0

```

### Really run the test

```bash
$ pytest

# or

$ python3 -m pytest

```
