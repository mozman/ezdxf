# Copyright (C) 2019, Manfred Moitzi
# License: MIT License
from ezdxf.tools import set_flag_state


def test_set_flag_state():
    assert set_flag_state(0, 1, True) == 1
    assert set_flag_state(0b10, 1, True) == 0b11
    assert set_flag_state(0b111, 0b010, False) == 0b101
    assert set_flag_state(0b010, 0b111, True) == 0b111
    assert set_flag_state(0b1111, 0b1001, False) == 0b0110
