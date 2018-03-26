# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.tableentries import UCS


@pytest.fixture
def ucs():
    return UCS.new('FFFF', dxfattribs={
        'name': 'UCS+90',
        'origin': (1.0, 1.0, 1.0),
        'xaxis': (0.0, 1.0, 0.0),
        'yaxis': (-1.0, 0.0, 0.0),
    })


def test_name(ucs):
    assert ucs.dxf.name == 'UCS+90'


def test_origin(ucs):
    assert ucs.dxf.origin == (1.0, 1.0, 1.0)


def test_xaxis(ucs):
    assert ucs.dxf.xaxis == (0.0, 1.0, 0.0)


def test_yaxis(ucs):
    assert ucs.dxf.yaxis == (-1.0, 0.0, 0.0)


def test_ucs(ucs):
    coords = ucs.ucs()
    assert coords.origin == (1, 1, 1)
    assert coords.ux == (0, 1, 0)
    assert coords.uy == (-1, 0, 0)
    assert coords.is_cartesian is True
