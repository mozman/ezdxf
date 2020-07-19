# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.validator import fix_lineweight


def test_lineweight_too_small():
    assert fix_lineweight(-4) == -1


def test_lineweight_too_big():
    assert fix_lineweight(212) == 211


def test_invalid_lineweight():
    assert fix_lineweight(10) == 13


