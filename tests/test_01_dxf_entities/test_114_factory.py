# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-18
import pytest
import ezdxf
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities import factory
from ezdxf.entities.factory import ENTITY_CLASSES


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


def test_registered_structural_entities():
    assert 'CLASS' in ENTITY_CLASSES
    assert 'TABLE' in ENTITY_CLASSES
    assert 'BLOCK' in ENTITY_CLASSES
    assert 'ENDBLK' in ENTITY_CLASSES


def test_registered_table_entries():
    assert 'LAYER' in ENTITY_CLASSES
    assert 'LTYPE' in ENTITY_CLASSES
    assert 'STYLE' in ENTITY_CLASSES
    assert 'DIMSTYLE' in ENTITY_CLASSES
    assert 'APPID' in ENTITY_CLASSES
    assert 'UCS' in ENTITY_CLASSES
    assert 'VIEW' in ENTITY_CLASSES
    assert 'VPORT' in ENTITY_CLASSES
    assert 'BLOCK_RECORD' in ENTITY_CLASSES


def test_new():
    e = factory.new('POINT')
    assert e.doc is None
    assert e.dxf.handle is None
    assert e.dxf.owner is None
    assert e.is_alive is True
    assert e.is_virtual is True


POINT = """0
POINT
5
FEFE
8
0
10
0.0
20
0.0
30
0.0
"""


def test_factory_load():
    tags = ExtendedTags.from_text(POINT)
    e = factory.load(tags)
    assert e.dxftype() == 'POINT'
    assert e.doc is None
    assert e.dxf.handle == 'FEFE'
    assert e.dxf.owner is None
    assert e.is_alive is True
    assert e.is_virtual is True


def test_bind_entity_to_doc(doc):
    e = factory.new('POINT')
    factory.bind(e, doc)
    assert e.doc is doc
    assert e.dxf.handle is not None, 'should have a handle'
    assert e.dxf.handle in doc.entitydb, 'should be stored in the entity database'
    assert e.dxf.owner is None, 'should not be linked to a layout or owner'
    assert e.is_virtual is False, 'is not a virtual entity'


def test_bind_entity_with_existing_handle_to_doc(doc):
    e = factory.new('POINT')
    e.dxf.handle = 'ABBA'
    factory.bind(e, doc)
    assert e.doc is doc
    assert e.dxf.handle == 'ABBA', 'should have the original handle'
    assert e.dxf.handle in doc.entitydb, 'should be stored in the entity database'


def test_bind_dead_entity_to_doc(doc):
    e = factory.new('POINT')
    e.destroy()
    with pytest.raises(AssertionError):
        factory.bind(e, doc)


def test_is_bound_true(doc):
    e = factory.new('POINT')
    factory.bind(e, doc)
    assert factory.is_bound(e, doc) is True
    assert e.is_bound is True


def test_is_bound_false(doc):
    e = factory.new('POINT')
    assert factory.is_bound(e, doc) is False
    assert e.is_bound is False


def test_if_destroyed_entity_is_bound(doc):
    e = factory.new('POINT')
    factory.bind(e, doc)
    e.destroy()
    assert factory.is_bound(e, doc) is False
    assert e.is_bound is False


def test_create_db_entry(doc):
    e = factory.create_db_entry('POINT', {}, doc)
    assert e.doc is doc
    assert e.dxf.handle is not None, 'should have a handle'
    assert e.dxf.handle in doc.entitydb, 'should be stored in the entity database'
    assert e.dxf.owner is None, 'should not be linked to a layout or owner'
    assert e.is_virtual is False, 'is not a virtual entity'


def test_unbind_bound_entity(doc):
    e = factory.create_db_entry('POINT', {}, doc)
    doc.modelspace().add_entity(e)
    factory.unbind(e)
    assert e.is_alive, 'should not be destroyed'
    assert e.is_virtual, 'should be virtual entity'
    assert e.doc is None
    assert e.dxf.owner is None
    assert e.dxf.handle is None


def test_unbind_unbound_entity(doc):
    e = factory.new('POINT')
    # should not raise an exception
    factory.unbind(e)
    assert e.is_alive, 'should not be destroyed'


def test_unbind_destroyed_entity(doc):
    e = factory.new('POINT')
    e.destroy()
    # should not raise an exception
    factory.unbind(e)
    assert e.is_alive is False
