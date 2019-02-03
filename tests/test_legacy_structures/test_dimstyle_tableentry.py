# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

import ezdxf
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


def test_set_blk1_and_blk2_arrows(dimstyle):
    dimstyle.set_arrows('', 'left_arrow', 'right_arrow')
    assert dimstyle.dxf.dimblk == ''
    assert dimstyle.dxf.dimblk1 == 'left_arrow'
    assert dimstyle.dxf.dimblk2 == 'right_arrow'


def test_set_both_arrows(dimstyle):
    dimstyle.set_arrows('arrow')
    assert dimstyle.dxf.dimblk == 'arrow'
    assert dimstyle.dxf.dimblk1 == ''
    assert dimstyle.dxf.dimblk2 == ''

    dimstyle.set_arrows(blk1='OPEN', blk2='DOT')
    assert dimstyle.dxf.dimblk == ''
    assert dimstyle.dxf.dimblk1 == 'OPEN'
    assert dimstyle.dxf.dimblk2 == 'DOT'


def test_set_tick(dimstyle):
    dimstyle.set_tick(.25)
    assert dimstyle.dxf.dimtsz == .25


def test_set_text_align(dimstyle):
    dimstyle.set_text_align(valign='above')
    assert dimstyle.dxf.dimtad == 1
    with pytest.raises(ezdxf.DXFVersionError):
        dimstyle.set_text_align(halign='above1')


def test_set_text_format(dimstyle):
    dimstyle.set_text_format(prefix='+', postfix=' cm', rnd=.5, leading_zeros=False, trailing_zeros=False)
    assert dimstyle.dxf.dimpost == '+<> cm'
    assert dimstyle.dxf.dimrnd == .5
    assert dimstyle.dxf.dimzin == 12
    with pytest.raises(ezdxf.DXFVersionError):
        dimstyle.set_text_format(dec=2)

