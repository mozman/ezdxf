# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.audit import Auditor

@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


def test_new_group(doc):
    msp = doc.modelspace()
    group = doc.groups.new('test1')
    with group.edit_data() as g:
        g.append(msp.add_point((0, 0)))
        g.append(msp.add_line((1, 1), (2, 2)))
    assert len(group) == 2
    assert group[0].dxftype() == 'POINT'
    assert group[1].dxftype() == 'LINE'
    assert len(list(group.handles())) == 2
    handle = group[0].dxf.handle
    assert handle in group

def test_unique_groups(doc):
    doc.groups.new('test2')
    with pytest.raises(ValueError):
        doc.groups.new('test2')


def test_modify_group(doc):
    msp = doc.modelspace()
    group = doc.groups.new('test3')
    with group.edit_data() as g:
        g.append(msp.add_point((0, 0)))
        g.append(msp.add_line((1, 1), (2, 2)))
    assert len(group) == 2
    e = [
        msp.add_point((3, 3)),
        msp.add_point((4, 4)),
    ]
    group.extend(e)
    assert len(group) == 4


def test_can_not_add_invalid_block_entities(doc):
    group = doc.groups.new('test4')
    block = doc.blocks.new("Block4")
    point = block.add_point((0, 0))
    with pytest.raises(ezdxf.DXFStructureError):
        with group.edit_data() as g:
            g.append(point)


def test_can_not_add_invalid_table_entry(doc):
    group = doc.groups.new('test5')
    layer = doc.layers.get("0")
    with pytest.raises(ezdxf.DXFStructureError):
        with group.edit_data() as g:
            g.append(layer)


def test_audit_filters_invalid_entities(doc):
    group = doc.groups.new('test6')
    msp = doc.modelspace()
    block = doc.blocks.new("Block6")
    point1 = block.add_point((0, 0))  # invalid BLOCK entity
    point2 = msp.add_point((0, 0))  # valid model space entity ...
    point2.destroy()  # ... but destroyed
    layer = doc.layers.get("0")  # invalid table entry

    group.extend([point1, point2, layer])
    auditor = Auditor(doc)
    group.audit(auditor)
    assert len(group) == 0


if __name__ == '__main__':
    pytest.main([__file__])
