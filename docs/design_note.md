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

------------------------------------------------

## Data structure

For **green hints**, just use a List of `None` and correct letters. Every non-none entry refers to the correct letter at the correct position.

For **yellow hints**, we use a dictionary of letter to map positions to exclude. Positions to exclude is a set of indices (integers). We can construct the list of possible locations easily from it.

The positions to exclude is very important. Note that the set does not include the location of other green hints. The green hint surely means we should exclude that position but we only **do that at the final stage**.

For **wrong hints**, we simply use a set.

In my design, letters in this set means they have **minimum and maximum length of 0** in the correct word.

Do not forget that wrong hint gives us the location to exclude for yellow hint in multi-letter cases. And thanks to the multi-letter cases, some letters may go between wrong or yellow in rounds.

We also have another dictionary known as **min max counter** to record the minimum and maximum length of a letter in the correct word.

```python
{"K": (1,3)} # This means K has min_count of 1 and max_count of 3 in correct answer
```

**Anything in wrong hints should not appear in this count dictionary.**

**In other words, each letter either belongs to green/yellow hint or wrong hint. And never in both sides.**

### About letters for blind guesses

Once we know the maximum count of a letter (by getting hint of G/Y and W at the same time), that letter needs to be excluded from blind guesses recommendation too.

In my design, these letters will be returned together with letters in **wrong hint** when requested (in function `letters_for_unknown_guess()`).

------------------------------------------------

## Verifications

There can be many copy and paste errors or simply users will just try random inputs. Therefore I try to write codes to verify the inputs.

### Basic rules

Users will supply us with many rounds of input. Each round has 2 strings, one is the guess (guess letters) and guess results (Green/Yellow/Wrong indicator).

Basic checking is implemented in `verify_hints()`, only check both guess and guess results have same length, guess has something (length >= 1) and only G/Y/W in result.

### Rules

So many things can go wrong. I try to include as much as I can...

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

    Let us assume the hint of first round is always correct. (No inconsistent single round hint like 4G1Y or 3Y for same letter). Further round hints should only be added if they are not contradictory to current accumulated hints.

    Logical rules:

    For wrong hint (not multiple letter case): (from the perspective of **round hint**)
    - Letters must not be in accmulated G/Y hints

    For yellow hint: (from the perspective of **round hint**)
    - Cannot be in the accmulated wrong hint
    - Cannot exclude the position for that green letter in accmulated green hint

    For green hint: (from the perspective of **round hint**)
    - If acc_green_hint[i] is known, round_green_hint[i] MUST BE equal to acc_green_hint[i]
    - Cannot be in the accmulated wrong hint
    - Cannot be excluded in accmulated yellow hint

    - Another way of saying the green hints is:
        1.)If the position result is green, the letter must be "that letter". AND
        2.)If "that letter" is at position X, the result must be green.
    - For position X: Invalid == (round_letters[x] == acc_letter[x]) XOR (round_pos_color[x] == GREEN)

    For each G/Y entry counter:
    - Count of each letter must be in range

    By the way remember that in single round, a position cannot be excluded in yellow hint and be correct as green hint at the same time.

------------------------------------------------

## How to handle yellow hints letter turns green later?

In normal Wordle game, we keep trying letters and we may have yellow letters. Then we make more guesses until we get all letters correct. We can see some letters goes from yellow to green in this case. **I call this Y->G.**

How would the code deal with this?

Originally I thought of "hint promotion" and delete the "old" yellow hint. However,this approach is not correct since yellow hints - the positions to exclude are always correct. So yellow hints should not be deleted at all.

(An error if we delete yellow hints then later hint report it is green at the same position)

So we simply just permanently store all the yellow hints (position to exclude).

When we build the combinations of yellow hints, we use the letter counter which take cares of both green and yellow hint to minus green hints to get the correct count of yellow hints.

------------------------------------------------

## From hints to letter, combinations pairs

Steps:

1. Exclude green hints positions. (Local variable for "globally excluded position")
1. For each green hint letter, reduce the min count in the counter. If counter reduced to 0, remove that entry in letter counter.
1. (Now letter counter only contains yellow hints) Generate combinations from counter and positions to exclude, including the green positions.
    - For example, "E" and remaining valid positions are {1,2,4} and the counter for "E" is 2. We will generate "E" with {1,2}, {2,4} and {1,4}
1. If valid combinations cannot be generated, then there must be problems with the inputs.

## From letter combinations pairs to correct pattern

Originally I thought of using Trie and "DFS search like" ideas to generate the correct patterns.

It is like :

1. choose a letter (the one with least combinations)
1. choose one of the combinations and queue up other combinations, exclude the used positions
1. prepare other unused letters
1. repeat first step for that unused letter
1. repeat until all letters are used

This way we know something is wrong if all positions are exclude for some letters.

Later I find that it quite troublesome - have to consider next nodes (all unused letters). That is not easy.

In the end, this idea is not much better than simply using "N-level nested for loop" and check if valid or not...

So I end up using simply bruteforce all combinations and check if there are not duplicated positions or not.

1. Get all letters and combinations
1. From each letter, choose 1 combination
1. If all indices unique (same as no repetitions on indices), it is valid pattern
1. Plug-in the combination with green hint to show correct pattern

------------------------------------------------

## Why return a generator for the patterns (instead of a list)?

The patterns can be very long (if it is longer version of Wordle like 9 letters). Returning a generator allows users to do more things with it, like using a word dictionary with the patterns generated.
