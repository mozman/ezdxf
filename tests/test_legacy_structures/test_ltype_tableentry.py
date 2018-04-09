# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.tableentries import Linetype


@pytest.fixture
def linetype():
    return Linetype.new('FFFF', dxfattribs={
        'name': 'TEST',
        'description': 'TESTDESC',
        'pattern': [0.2, 0.1, -0.1]
    })


def test_name(linetype):
    assert linetype.dxf.name == 'TEST'


def test_description(linetype):
    assert linetype.dxf.description == 'TESTDESC'


def test_pattern_items_count(linetype):
    def count_items():
        return len(linetype.tags.noclass.find_all(49))

    assert linetype.dxf.items == 2
    assert linetype.dxf.items == count_items()


def test_pattern_length(linetype):
    assert linetype.dxf.length == .2
