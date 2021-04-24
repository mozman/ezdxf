#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import MTextEditor


def test_append_text():
    m = MTextEditor()
    m.append('TEXT')
    assert m.text == "TEXT"


def test_iadd_text():
    m = MTextEditor()
    m += 'TEXT'
    assert m.text == "TEXT"


def test_stacked_text():
    m = MTextEditor()
    m.stacked_text('1', '2')
    assert m.text == r"\S1^ 2;"


def test_change_color():
    m = MTextEditor()
    m.change_color('red')
    assert m.text == r"\C1"


def test_change_font():
    m = MTextEditor()
    m.change_font('kroeger', bold=False, italic=False, codepage='238',
                  pitch=10)
    assert m.text == r"\Fkroeger|b0|i0|c238|p10;"


def test_fluent_interface():
    m = MTextEditor(
        "some text").change_color('red').stacked_text('1', '2').append("end.")
    assert m.text == r"some text\C1\S1^ 2;end."


if __name__ == '__main__':
    pytest.main([__file__])
