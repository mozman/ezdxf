# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.legacy.tableentries import View


@pytest.fixture
def view():
    return View.new('FFFF', dxfattribs={
        'name': 'VIEW1',
        'flags': 0,
        'height': 1.0,
        'width': 1.0,
        'center_point': (0, 0),
        'direction_point': (0, 0, 0),
        'target_point': (0, 0, 0),
        'lens_length': 1.0,
        'front_clipping': 0.0,
        'back_clipping': 0.0,
        'view_twist': 0.0,
        'view_mode': 0,
    })


def test_view_attribute_access(view):
    assert view.dxf.name == 'VIEW1'
    assert view.dxf.flags == 0
    assert view.dxf.height == 1.0
    assert view.dxf.width == 1.0
    assert view.dxf.center_point == (0, 0)
    assert view.dxf.direction_point == (0, 0, 0)
    assert view.dxf.target_point == (0, 0, 0)
    assert view.dxf.lens_length == 1.0
    assert view.dxf.front_clipping == 0
    assert view.dxf.back_clipping == 0
    assert view.dxf.view_twist == 0
    assert view.dxf.view_mode == 0
