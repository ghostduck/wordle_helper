# Design Notes

This is like an explanation to codebreaker for Wordle design.

## Hint interpretation

This is about the input of the program.

Let say we our guess **"BOCCH"**. I call **C** is the multi-letter guess.

We have these outcome of guesses:

- Green hints: Correct letter and correct position. Other guesses should not use this position.

- Yellow hint: Correct letter but wrong position. This means this letter is in the correct word and we should consider other positions. And don't forget it is possible to have more of this letter - unless there is a wrong hint indicator for this letter.

- Wrong hint (Single): No such letter in correct word.

- Wrong hints (Multi): This is slightly tricky. If all the letters are wrong, this is the same as single wrong hint case (no such letter). Otherwise (there are some green and/or yellow result of the same letter), it is telling us: 1. the maximum amount of the letter in target word and 2. the position to exclude.

Basically, every hint is telling us more things to exclude.

## Data structure

For **green hints**, just use a List of `None` and correct letters. Every non-none entry refers to the correct letter.

For **yellow hints**, we use a dictionary of letter to positions to exclude. Positions to exclude is a set of indices (integers). We can construct the list of possible locations easily from it.

The positions to exclude is very important. Note that it does not include the location of other green hints. The green hint surely means we should exclude that position but we only **do that at the final stage**.

For **wrong hint**s, we simply use a set.

In my design, letters in this set means they have **maximum and minimum length of 0** in the correct word.

Do not forget that wrong hint gives us the location to exclude for yellow hint in multi-letter cases. And thanks to the multi-letter cases, some letters may go between wrong or yellow in rounds.

We also have another dictionary known as **min max counter** to record the minimum and maximum length of a letter in the correct word.

```python
{"K": (1,3)} # This means K has min_count of 1 and max_count of 3 in correct answer
```

**Anything in wrong hints should not appear in this count dictionary.**

**In other words, each letter either belongs to green/yellow hint or wrong hint. And never in both sides.**

### About letters for blind guesses

Once we know the maximum count of a letter (by getting hint of G/Y and W at the same time), that letter needs to be excluded from blind guesses recommendation too.

In my design, these letter will be returned together with letters in *wrong hint* when requested (in function call).

------------------------------------------------

## Verifications

Verify single round hint then verify against global(accumulated) hints.

I am trying my best to include all the impossible / contradictory cases with as fewer rules as I can think of.

### Rules

1. Number of letter hints (letter and locations to exclude) **MUST NOT** be greater than the whole length

    - Reason: Assume 5 letter normal Wordle game. We at most have 5 green hints or 5 yellow hints (letter and location to exclude pair). Even when we consider hints for multi-rounds, there are no way we can have 6 yellow/green hints of different letters.

    - Example: ABCDE returns all yellow. Then we have hint of FGHIJ and one of them is yellow. No way these hints are valid.

1. Summation of hints' min_count **MUST NOT** be greater than the whole length

    Reason: Similar to the rule above. The number of characters must be within the limit. Actually this rule already covers the rule above if all the min_count is valid.

1. Each letter's min_count **MUST** match (smaller or equal to) the length of possible locations. And it must be >=1.

    Example: Check the case of AAABC and YYYWW. With length of 5 and 3A's in the "wrong" location - we have to fit 3A's in location of [3,4] (zero-based) only. That does not make sense.

    Also this covers case of excluding too many locations (by mistake?). Like TBCDE and YGGGG. T has no valid locations but with min_count of 1.

1. Inconsistent hints (multi-round)

    Slightly difficult to generalize. This is refering to contradictory hints.

    Examples:

    - Same letter at the same position changes from G to B/W in rounds
    - Same letter at the same position changes from B/W to G in rounds
    - Single letter case: same position changes from B/W to something else in rounds
    - Change of min_count is out of range

    Try to show another example from the perspective of data:

    - green_hints: be consistent between rounds (B/W to G, G to B/W changes)
    - y_w_hint_excluded_position: allow to add new entries of letter, just add more to existing range as long as other checks are OK
    - wrong_letters: Can only be greater (previous set must be subset of current set)
    - letter_min_max_counter: allow to add new entries of letter, existing min can increase and max can decrease but must be consistent and within old range. Do not forget non-hard mode Wordle game case: new round hints no need to follow previous hints. So as long as the min_count is within the range, that hint is "not wrong" but we probably ignore the count hint

## How to handle yellow hints letter turns green later?

## From hints to letter, combinations pairs

Steps:

1. Exclude green hints positions. (Local variable for "globally excluded position")
1. For each green hint letter, reduce the min count in the counter. If counter reduced to 0, remove that entry in counter and y_w_hint_excluded_position.
1. Generate combinations from counter and positions to exclude, including the green positions.
    - For example, "E" and remaining valid positions are {1,2,4} and the counter for "E" is 2. We will generate "E" with {1,2}, {2,4} and {1,4}
1. If valid combinations cannot be generated, then there must be problems with the inputs.

## Loop inside the stack

Like a DFS search but we have to loop everything anyway. Yield that stack when all hints are used.
