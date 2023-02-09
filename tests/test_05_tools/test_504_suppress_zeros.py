# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

from ezdxf.tools import suppress_zeros


def test_leading_zeros():
    assert suppress_zeros("0") == "0"
    assert suppress_zeros("0.", leading=True, trailing=True) == "0"
    assert suppress_zeros("0.0", leading=True, trailing=True) == "0"
    assert suppress_zeros(".0", leading=True, trailing=True) == "0"
    assert suppress_zeros("-.0", leading=True, trailing=True) == "0"
    assert suppress_zeros("+.0", leading=True, trailing=True) == "0"

    assert suppress_zeros("0.0", leading=False, trailing=True) == "0"
    assert suppress_zeros("0.1", leading=False, trailing=True) == "0.1"
    assert suppress_zeros("1.0", leading=False, trailing=True) == "1"
    assert suppress_zeros("1.0000", leading=False, trailing=True) == "1"
    assert suppress_zeros("-1.", leading=False, trailing=True) == "-1"

    assert suppress_zeros("0.10", leading=True, trailing=False) == ".10"
    assert suppress_zeros("-0.10", leading=True, trailing=False) == "-.10"
    assert suppress_zeros("+000.10", leading=True, trailing=False) == "+.10"


def test_trim_trailing_zeros_for_integers():
    assert suppress_zeros("0", trailing=True) == "0"
    assert suppress_zeros("1", trailing=True) == "1"
    assert suppress_zeros("-1", trailing=True) == "-1"
    assert suppress_zeros("10", trailing=True) == "10"
    assert suppress_zeros("-10", trailing=True) == "-10"
