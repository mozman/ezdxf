#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import MTextFormatter


def test_append_text():
    fmt = MTextFormatter()
    fmt.append('TEXT')
    assert fmt.text == "TEXT"


def test_iadd_text():
    fmt = MTextFormatter()
    fmt += 'TEXT'
    assert fmt.text == "TEXT"


def test_stacked_text():
    fmt = MTextFormatter()
    fmt.stacked_text('1', '2')
    assert fmt.text == r"\S1^ 2;"


def test_change_color():
    fmt = MTextFormatter()
    fmt.change_color('red')
    assert fmt.text == r"\C1"


def test_change_font():
    fmt = MTextFormatter()
    fmt.change_font('kroeger', bold=False, italic=False, codepage='238',
                    pitch=10)
    assert fmt.text == r"\Fkroeger|b0|i0|c238|p10;"


def test_fluent_interface():
    fmt = MTextFormatter(
        "some text").change_color('red').stacked_text('1', '2').append("end.")
    assert fmt.text == r"some text\C1\S1^ 2;end."


if __name__ == '__main__':
    pytest.main([__file__])
