# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entitydb import EntityDB
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.audit import Auditor

ENTITY = DXFEntity.from_text("0\nTEST\n5\nFFFF\n")
auditor = Auditor(None)


@pytest.fixture
def db():
    db = EntityDB()
    db['FEFE'] = ENTITY
    return db


def test_get_value(db):
    assert ENTITY is db['FEFE']


def test_set_value(db):
    new_entity = DXFEntity.from_text("0\nTEST\n5\nFFFF\n")
    db['FEFE'] = new_entity
    assert new_entity is db['FEFE']


def test_del_value(db):
    del db['FEFE']
    with pytest.raises(KeyError):
        _ = db['FEFE']
    assert len(db) == 0


def test_keys(db):
    assert list(db.keys()) == ['FEFE']


def test_values(db):
    assert list(db.values()) == [ENTITY]


def test_items(db):
    assert list(db.items()) == [('FEFE', ENTITY)]


def test_get(db):
    assert db.get('ABCD') is None


def test_add_tags():
    db = EntityDB()
    db.add(ENTITY)
    assert 'FFFF' in db


def test_len(db):
    assert len(db) == 1


def test_restore_integrity_purge():
    db = EntityDB()
    e = DXFEntity.from_text("0\nTEST\n5\nABBA\n")
    db.add(e)
    assert len(db) == 1
    db.audit(auditor)
    assert len(db) == 1
    e.destroy()
    db.audit(auditor)
    assert len(db) == 0


def test_restore_integrity_recover():
    db = EntityDB()
    e = DXFEntity.from_text("0\nTEST\n5\nABBA\n")
    db.add(e)
    assert len(db) == 1

    # modify handle
    e.dxf.handle = 'FEFE'
    assert 'ABBA' in db
    assert 'FEFE' not in db

    db.audit(auditor)
    assert len(db) == 1
    assert 'FEFE' in db
    assert 'ABBA' not in db


def test_restore_integrity_remove_invalid_None():
    db = EntityDB()
    e = DXFEntity.from_text("0\nTEST\n5\nABBA\n")
    db.add(e)
    assert len(db) == 1

    # set invalid handle
    e.dxf.handle = None
    db.audit(auditor)
    assert len(db) == 0


def test_restore_integrity_remove_invalid_handle():
    db = EntityDB()
    e = DXFEntity.from_text("0\nTEST\n5\nABBA\n")
    db.add(e)
    assert len(db) == 1

    # set invalid handle
    e.dxf.handle = 'XFFF'
    db.audit(auditor)
    assert len(db) == 0
