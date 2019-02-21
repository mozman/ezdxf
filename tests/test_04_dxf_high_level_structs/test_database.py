# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.database import EntityDB
from ezdxf.lldxf.extendedtags import ExtendedTags

ENTITY = ExtendedTags.from_text("0\nTEST\n5\nFFFF\n")


@pytest.fixture
def db():
    db = EntityDB()
    db['0'] = ENTITY
    return db


def test_get_value(db):
    assert ENTITY is db['0']


def test_set_value(db):
    new_entity = ExtendedTags.from_text("0\nTEST\n5\nFFFF\n")
    db['0'] = new_entity
    assert new_entity is db['0']


def test_del_value(db):
    del db['0']
    with pytest.raises(KeyError):
        _ = db['0']
    assert len(db) == 0


def test_keys(db):
    assert list(db.keys()) == ['0']


def test_values(db):
    assert list(db.values()) == [ENTITY]


def test_items(db):
    assert list(db.items()) == [('0', ENTITY)]


def test_get(db):
    assert db.get('ABCD') is None


def test_add_tags():
    db = EntityDB()
    db.add_tags(ENTITY)
    assert 'FFFF' in db


def test_len(db):
    assert len(db) == 1
