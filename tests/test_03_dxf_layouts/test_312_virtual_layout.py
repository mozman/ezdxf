# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf.audit import Auditor


@pytest.fixture
def layout():
    return VirtualLayout()


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


def test_add_simple_entities(layout):
    layout.add_line(start=(0, 0), end=(1, 0))
    layout.add_circle(center=(0, 0), radius=2)
    layout.add_point(location=(0, 0))
    assert len(layout) == 3


def test_entities_have_no_handle(layout):
    layout.add_point(location=(0, 0))
    entity = layout[0]
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None
    assert entity.doc is None


def test_removing_entiy_does_not_destroy_entity(layout):
    point = layout.add_point(location=(0, 0))
    layout.delete_entity(point)
    assert len(layout) == 0
    assert point.is_alive


def test_can_not_add_entity_to_a_real_layout(layout, doc):
    msp = doc.modelspace()
    point = layout.add_point(location=(0, 0))
    with pytest.raises(ezdxf.DXFStructureError):
        msp.add_entity(point)


def test_copy_all_entities_to_a_real_layout(layout, doc):
    msp = doc.modelspace()
    point = layout.add_point(location=(0, 0))
    layout.copy_all_to_layout(msp)
    copy = msp[-1]
    assert len(layout) == 1, 'do not remove from virtual layout'
    assert point is not copy, 'entity should be copied'
    assert copy.doc is doc, 'copy should be assigned to DXF document'
    assert copy.dxf.handle is not None, 'copy should have a handle'
    assert copy.dxf.owner == msp.layout_key, 'copy should have new layout as owner'
    assert copy.dxf.handle in doc.entitydb, 'copy should be stored in document entity database'


def test_move_all_entities_to_a_real_layout(layout, doc):
    msp = doc.modelspace()
    point = layout.add_point(location=(0, 0))
    layout.move_all_to_layout(msp)
    entity = msp[-1]
    assert len(layout) == 0, 'remove from virtual layout'
    assert point is entity
    assert entity.doc is doc, 'entity should be assigned to DXF document'
    assert entity.dxf.handle is not None, 'entity should have a handle'
    assert entity.dxf.owner == msp.layout_key, 'entity should have new layout as owner'
    assert entity.dxf.handle in doc.entitydb, 'entity should be stored in document entity database'


def test_copy_all_sub_entities_to_a_real_layout(layout, doc):
    msp = doc.modelspace()
    polyline = layout.add_polyline3d([(0, 0), (1, 0), (1, 1)])
    len_db = len(doc.entitydb)
    layout.copy_all_to_layout(msp)
    copy = msp[-1]
    assert len(layout) == 1, 'do not remove from virtual layout'
    assert polyline is not copy, 'entity should be copied'
    assert copy.doc is doc, 'copy should be assigned to DXF document'
    assert len(doc.entitydb) == len_db + 5, 'copy main- and sub-entities + seqend'
    assert copy.dxf.handle is not None, 'copy should have a handle'
    assert copy.dxf.owner == msp.layout_key, 'copy should have new layout as owner'
    assert copy.dxf.handle in doc.entitydb, 'copy should be stored in document entity database'
    # check sub-entities
    vertex = copy.vertices[0]
    assert vertex.doc is doc, 'vertices should have document'
    assert vertex.dxf.handle in doc.entitydb, 'vertices should be stored in the entity database'
    # check sub-entities
    assert copy.seqend.doc is doc, 'seqend should have document'
    assert copy.seqend.dxf.handle in doc.entitydb, 'seqend be stored in the entity database'

    auditor = Auditor(doc)
    copy.audit(auditor)
    assert len(auditor.errors) == 0
    assert len(auditor.fixes) == 0


def test_move_all_sub_entities_to_a_real_layout(layout, doc):
    msp = doc.modelspace()
    polyline = layout.add_polyline3d([(0, 0), (1, 0), (1, 1)])
    len_db = len(doc.entitydb)
    layout.move_all_to_layout(msp)
    entity = msp[-1]
    assert len(layout) == 0, 'remove from virtual layout'
    assert polyline is entity
    assert entity.doc is doc, 'entity should be assigned to DXF document'
    assert len(doc.entitydb) == len_db + 5, 'add main- and sub-entities + seqend'
    assert entity.dxf.handle is not None, 'entity should have a handle'
    assert entity.dxf.owner == msp.layout_key, 'entity should have new layout as owner'
    assert entity.dxf.handle in doc.entitydb, 'entity should be stored in document entity database'
    # check sub-entities
    vertex = entity.vertices[0]
    assert vertex.doc is doc, 'vertices should have document'
    assert vertex.dxf.handle in doc.entitydb, 'vertices should be stored in the entity database'
    # check sub-entities
    assert entity.seqend.doc is doc, 'seqend should have document'
    assert entity.seqend.dxf.handle in doc.entitydb, 'seqend be stored in the entity database'

    auditor = Auditor(doc)
    entity.audit(auditor)
    assert len(auditor.errors) == 0
    assert len(auditor.fixes) == 0


if __name__ == '__main__':
    pytest.main([__file__])
