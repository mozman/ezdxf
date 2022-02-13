# Copyright (c) 2011-2022, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entitydb import EntityDB
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.audit import Auditor

ENTITY = DXFEntity.new(handle="FFFF")
auditor = Auditor(ezdxf.new())


@pytest.fixture
def db():
    db = EntityDB()
    db["FEFE"] = ENTITY
    return db


def test_get_value(db):
    assert ENTITY is db["FEFE"]


def test_set_value(db):
    new_entity = DXFEntity.new(handle="FEFE")
    db["FEFE"] = new_entity
    assert new_entity is db["FEFE"]


def test_del_value(db):
    del db["FEFE"]
    with pytest.raises(KeyError):
        _ = db["FEFE"]
    assert len(db) == 0


def test_delete_entity():
    db = EntityDB()
    entity = DXFEntity()
    db.add(entity)
    assert len(db) == 1
    db.delete_entity(entity)
    assert len(db) == 0


def test_delete_dead_entity_entity():
    db = EntityDB()
    entity = DXFEntity.new(handle="FEFE")
    db.add(entity)
    assert len(db) == 1
    entity.destroy()
    # delete_entity() should not raise an error if entity is not alive!
    db.delete_entity(entity)
    # but entity.destroy() does not remove entity from EntityDB!
    assert "FEFE" in db
    assert len(db) == 1
    # Auditor() removes such dead entities from database see test_restore_integrity_purge()


def test_keys(db):
    assert list(db.keys()) == ["FEFE"]


def test_values(db):
    assert list(db.values()) == [ENTITY]


def test_items(db):
    assert list(db.items()) == [("FEFE", ENTITY)]


def test_get(db):
    assert db.get("ABCD") is None


def test_add_tags():
    db = EntityDB()
    db.add(ENTITY)
    assert "FFFF" in db


def test_len(db):
    assert len(db) == 1


def test_restore_integrity_purge():
    db = EntityDB()
    e = DXFEntity.new()
    db.add(e)
    assert len(db) == 1
    db.audit(auditor)
    assert len(db) == 1
    e.destroy()
    db.audit(auditor)
    assert len(db) == 0


def test_restore_integrity_recover():
    db = EntityDB()
    e = DXFEntity.new(handle="ABBA")
    db.add(e)
    assert len(db) == 1

    # modify handle
    e.dxf.handle = "FEFE"
    assert "ABBA" in db
    assert "FEFE" not in db

    db.audit(auditor)
    assert len(db) == 1
    assert "FEFE" in db
    assert "ABBA" not in db


def test_restore_integrity_remove_invalid_None():
    db = EntityDB()
    e = DXFEntity.new()
    db.add(e)
    assert len(db) == 1

    # set invalid handle
    e.dxf.handle = None
    db.audit(auditor)
    assert len(db) == 0


def test_restore_integrity_remove_invalid_handle():
    db = EntityDB()
    e = DXFEntity.new(handle="ABBA")
    db.add(e)
    assert len(db) == 1

    # set invalid handle
    e.dxf.handle = "XFFF"
    db.audit(auditor)
    assert len(db) == 0


def test_add_entity_multiple_times():
    db = EntityDB()
    e = DXFEntity()
    db.add(e)
    handle = e.dxf.handle
    assert len(db) == 1

    db.add(e)
    assert e.dxf.handle == handle, "handle must not change"
    assert len(db) == 1, "do not store same entity multiple times"


def test_discard_contained_entity():
    db = EntityDB()
    e = DXFEntity()
    db.add(e)
    assert len(db) == 1
    db.discard(e)
    assert len(db) == 0
    assert e.dxf.handle is None


def test_discard_entity_with_none_handle():
    db = EntityDB()
    e = DXFEntity()
    assert e.dxf.handle is None
    # call should not raise any Exception
    db.discard(e)
    # 2rd call should not raise any Exception
    db.discard(e)


def test_discard_entity_with_handle_not_in_database():
    db = EntityDB()
    e = DXFEntity()
    e.dxf.handle = "ABBA"
    assert e.dxf.handle not in db
    # call should not raise any Exception
    db.discard(e)
    # 2rd call should not raise any Exception
    db.discard(e)
    assert (
        e.dxf.handle is "ABBA"
    ), "set handle to None, only if entity was removed"


def test_trashcan_context_manager():
    db = EntityDB()
    entities = [DXFEntity() for _ in range(5)]
    for e in entities:
        db.add(e)
    handles = list(db.keys())
    with db.trashcan() as trashcan:
        trashcan.add(handles[0])
        trashcan.add(handles[1])

    assert len(db) == 3
    assert entities[0].is_alive is False
    assert entities[1].is_alive is False


def test_reset_entity_handle():
    db = EntityDB()
    entity = DXFEntity()
    db.add(entity)
    assert db.reset_handle(entity, "FEFE") is True
    assert entity.dxf.handle == "FEFE"
    assert "FEFE" in db


def test_can_not_reset_entity_handle():
    """Can not reset the DXF handle of an entity to a handle, which is already
    used by another entity.
    """
    db = EntityDB()
    entity1 = DXFEntity()
    entity2 = DXFEntity()
    db.add(entity1)
    db.add(entity2)
    handle = entity1.dxf.handle

    assert db.reset_handle(entity1, entity2.dxf.handle) is False
    assert entity1.dxf.handle == handle


def test_query_method_exist():
    db = EntityDB()
    db.add(DXFEntity())
    db.add(DXFEntity())
    assert len(db.query()) == 2
