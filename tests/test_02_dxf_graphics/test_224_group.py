# Copyright (c) 2015-2024, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope="module")
def groups():
    doc = ezdxf.new("R2000")
    return doc.groups


def test_group_table_is_empty(groups):
    assert 0 == len(groups)


def test_create_new_group(groups):
    g = groups.new("MyGroup", description="The group description.")
    assert "GROUP" == g.dxftype()
    assert "MyGroup" in groups
    assert 0 == g.dxf.unnamed, "Named group has wrong unnamed attribute."
    assert 1 == g.dxf.selectable, "Group should be selectable by default."
    assert "The group description." == g.dxf.description
    assert 1 == len(groups)
    groups.clear()
    assert 0 == len(groups)


def test_create_unnamed_group(groups):
    g = groups.new()
    assert "GROUP" == g.dxftype()
    assert "*A1" in groups
    assert 1 == g.dxf.unnamed, "Unnamed group has wrong unnamed attribute."
    assert 1 == g.dxf.selectable, "Group should be selectable by default."
    assert "" == g.dxf.description, "Group description should be '' by default."
    assert 1 == len(groups)
    groups.clear()
    assert 0 == len(groups)


def test_delete_group_by_entity(groups):
    assert len(groups) == 0
    g = groups.new("MyGroup")
    assert len(groups) == 1
    groups.delete(g)
    assert len(groups) == 0


def test_delete_group_by_name(groups):
    assert "MyGroup" not in groups
    groups.new("MyGroup")
    groups.delete("MyGroup")
    assert 0 == len(groups)


def test_add_entities():
    dwg = ezdxf.new("R2000")
    group = dwg.groups.new()
    # the group itself is not an entity space, DXF entities has to be placed in model space, paper space
    # or in a block
    msp = dwg.modelspace()
    with group.edit_data() as e:  # e is a standard Python list of DXF entities
        line = msp.add_line((0, 0), (3, 0))
        e.append(line)
        e.append(msp.add_circle((0, 0), radius=2))

    assert len(group) == 2
    assert line in group

    group_handle = group.dxf.handle
    for entity in group:
        assert (
            group_handle in entity.reactors
        ), "expected group handle as reactor in entity"

    group.clear()
    assert len(group) == 0
    assert (
        group_handle not in line.reactors
    ), "group handle has to be removed from reactors"


def test_extend_group():
    dwg = ezdxf.new("R2000")
    group = dwg.groups.new()
    group_handle = group.dxf.handle
    # the group itself is not an entity space, DXF entities has to be placed in model space, paper space
    # or in a block
    msp = dwg.modelspace()
    line = msp.add_line((0, 0), (3, 0))
    group.set_data([line])
    assert len(group) == 1

    line2 = msp.add_line((0, 0), (3, 0))
    group.extend([line2])
    assert len(group) == 2
    assert group_handle in line2.reactors, "expected group handle as reactor in entity"

    group.extend([line])
    assert len(group) == 2, "cannot add same entity a second time"


if __name__ == "__main__":
    pytest.main([__file__])
