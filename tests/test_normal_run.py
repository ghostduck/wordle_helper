
import pytest

from wordle_helper.wordle_no_spoiler_helper import process_all_hints

# To be honest I should really create a case manually and get the possible combinations by hand. But I am too lazy... So I copy the output instead. Hopefully my (simple) algorithm is correct and therefore the output and the test is correct.

rupee_test = [
    # Possible patterns: REP?E, R?PEE
    # P must be at 3rd therefore R at 1st only
    ("PRIDE","YYWWG"),
    ("SPARE","WYWYG"),
    ("CREPE","WYYYG"),
]
rupee_test_out = ["REP*E", "R*PEE"]

silly_rupee_test = [
    ("PRIDE","YYWWG"),
    ("SPARE","WYWYG"),
    ("RUPEE","GGGGG"),  # Silly fake case by adding the correct answer before last guess
    ("CREPE","WYYYG"),
]

silly_rupee_test_out = ["RUPEE"]

scold_test = [
    ("CROSS","YWGYW"),
    ("STOIC","GWGWY"),
    ("SHOCK","GWGYW"),
    #("SCOPE","GGGWW"),
]

scold_test_out = ["SCO**"]

flair_test = [
    # Possible patterns: RFAI?, RA?IF, R?AIF, RFA?I, RF?AI, RA?FI, R?AFI, FA?IR, F?AIR, AF?IR, ?FAIR
    ("PRIDE", "WYYWW"),
    ("BIRTH", "WYYWW"),
    ("INFRA", "YWYYY"),
]
flair_test_out = ['RFAI*', 'RA*IF', 'R*AIF', 'RFA*I', 'RF*AI', 'RA*FI', 'R*AFI', 'FA*IR', 'F*AIR', 'AF*IR', '*FAIR']

flair_test2 = [
    # Only possible pattern: F?AIR
    ("PRIDE", "WYYWW"),
    ("BIRTH", "WYYWW"),
    ("INFRA", "YWYYY"),
    ("FAIRY", "GYYYW"),
]
flair_test2_out = ["F*AIR"]

gamer_test = [
# Only possible pattern - ?AMER
("PRIDE", "WYWWY"),
("MUTER", "YWWGG"),
("AMBER", "YYWGG"),
]
gamer_test_out = ["*AMER"]


@pytest.mark.parametrize("test_input, expected", [
    (rupee_test, rupee_test_out),
    (flair_test, flair_test_out),
    (flair_test2, flair_test2_out),
    (gamer_test, gamer_test_out),
    (silly_rupee_test, silly_rupee_test_out),
    (scold_test, scold_test_out),
],
ids=["NORMAL_RUPEE", "NORMAL_FLAIR1", "NORMAL_FLAIR2", "NORMAL_GAMER", "SILLY_RUPEE", "NORMAL_SCOLD"])
def test_generate_correct_pattern(test_input, expected):
    # Order in each expected output does not matter
    # They are output from generator. But I expect no duplicate from it.
    # So do not convert them to a set
    gen, _ = process_all_hints(test_input, unknown_mark="*")
    pattern_output_lst = [s for s in gen]

    pattern_output_lst.sort()
    expected.sort()
    assert pattern_output_lst == expected
