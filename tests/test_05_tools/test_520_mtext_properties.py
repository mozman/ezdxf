#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import MTextProperties


def test_underline():
    p = MTextProperties()
    assert p.underline is False
    p.underline = True
    assert p.underline is True


def test_strike():
    p = MTextProperties()
    assert p.strike is False
    p.strike = True
    assert p.strike is True


def test_overstrike():
    p = MTextProperties()
    assert p.overstrike is False
    p.overstrike = True
    assert p.overstrike is True


def test_copy():
    p = MTextProperties()
    p.underline = True
    p2 = p.copy()
    p2.underline = False
    assert p != p2


def test_equality():
    p = MTextProperties()
    p.underline = True
    p2 = MTextProperties()
    p2.underline = True
    assert p == p2


def test_set_aci():
    p = MTextProperties()
    p.rgb = (0, 1, 2)
    p.aci = 7
    assert p.aci == 7
    assert p.rgb is None, "should reset rgb value"


if __name__ == '__main__':
    pytest.main([__file__])
