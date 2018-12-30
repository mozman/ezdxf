# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.tableentries import DimStyle

@pytest.fixture
def dimstyle():
    return DimStyle.new('FFFF', dxfattribs={
        'name': 'DIMSTYLE1',
    })


def test_name(dimstyle):
    assert 'DIMSTYLE1' == dimstyle.dxf.name


def test_handle_code(dimstyle):
    assert 'FFFF' == dimstyle.tags.noclass.get_first_value(105), 'expected group code 105 handle'


def test_set_blk1_and_blk2_ticks(dimstyle):
    dimstyle.set_ticks('', 'left_arrow', 'right_arrow')
    assert dimstyle.dxf.dimblk == ''
    assert dimstyle.dxf.dimblk1 == 'left_arrow'
    assert dimstyle.dxf.dimblk2 == 'right_arrow'


def test_set_both_ticks(dimstyle):
    dimstyle.set_ticks('arrow')
    assert dimstyle.dxf.dimblk == 'arrow'
    assert dimstyle.dxf.dimblk1 == 'arrow'
    assert dimstyle.dxf.dimblk2 == 'arrow'
