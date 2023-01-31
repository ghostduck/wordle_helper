
import pytest

from wordle_helper.wordle_no_spoiler_helper import process_all_hints

rupee_test = [
    # Possible patterns: REP?E, R?PEE
    ("PRIDE","YYWWG"),
    ("SPARE","WYWYG"),
    ("CREPE","WYYYG"),
]
rupee_test_out = ["REP*E", "R*PEE"]

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
    (gamer_test, gamer_test_out)
],
ids=["NORMAL_RUPEE", "NORMAL_FLAIR1", "NORMAL_FLAIR2", "NORMAL_GAMER"])
def test_generate_correct_pattern(test_input, expected):
    # Order in each expected output does not matter
    # They are output from generator. But I expect no duplicate from it.
    # So do not convert them to a set
    gen, _ = process_all_hints(test_input, unknown_mark="*")
    pattern_output_lst = [s for s in gen]

    pattern_output_lst.sort()
    expected.sort()
    assert pattern_output_lst == expected
