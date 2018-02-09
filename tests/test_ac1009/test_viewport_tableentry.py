# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.legacy.tableentries import VPort


@pytest.fixture
def vport():
    return VPort.new('FFFF', dxfattribs={
        'name': 'VP1',
    })


def test_name(vport):
    assert vport.dxf.name == 'VP1'
