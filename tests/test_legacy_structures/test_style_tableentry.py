# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.tableentries import Style


@pytest.fixture
def style():
    return Style.new('FFFF', dxfattribs={
        'name': 'TEST',
        'font': 'NOFONT.ttf',
        'width': 2.0,
    })


def test_name(style):
    assert 'TEST' == style.dxf.name


def test_font(style):
    assert 'NOFONT.ttf' == style.dxf.font


def test_width(style):
    assert 2.0 == style.dxf.width


def test_height(style):
    assert 0.0 == style.dxf.height


def test_oblique(style):
    assert 0.0 == style.dxf.oblique


def test_bigfont(style):
    assert '' == style.dxf.bigfont
