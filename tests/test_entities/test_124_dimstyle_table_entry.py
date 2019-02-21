# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.dimstyle import DimStyle
from ezdxf.drawing2 import Drawing


@pytest.fixture
def dimstyle():
    doc = Drawing.new()
    doc.blocks.new('left_arrow')
    doc.blocks.new('right_arrow')
    doc.blocks.new('arrow')
    doc.blocks.new('_DOT')
    doc.blocks.new('_OPEN')
    return DimStyle.new('FFFF', doc=doc, dxfattribs={
        'name': 'DIMSTYLE1',
    })


def test_name(dimstyle):
    assert 'DIMSTYLE1' == dimstyle.dxf.name


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


def test_set_text_format(dimstyle):
    dimstyle.set_text_format(prefix='+', postfix=' cm', rnd=.5, leading_zeros=False, trailing_zeros=False)
    assert dimstyle.dxf.dimpost == '+<> cm'
    assert dimstyle.dxf.dimrnd == .5
    assert dimstyle.dxf.dimzin == 12

