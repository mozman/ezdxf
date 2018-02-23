# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

import ezdxf
from ezdxf.database import EntityDB


@pytest.fixture
def db():
    db = EntityDB()
    db[0] = 'TEST'
    return db


def test_get_value(db):
    assert 'TEST' == db[0]


def test_set_value(db):
    db[0] = 'XTEST'
    assert 'XTEST' == db[0]


def test_del_value(db):
    del db[0]
    with pytest.raises(KeyError):
        db[0]


@pytest.fixture(params=['R12', 'R2000'], scope='module')
def dwg(request):
    return ezdxf.new(request.param)


def test_duplicate_simple_entity(dwg):
    pass


def test_duplicate_polyline_entity(dwg):
    pass


def test_duplicate_insert_with_attribs_entity(dwg):
    pass

