# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entities.leader import Leader
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.layouts import VirtualLayout
from ezdxf.protocols import SupportsVirtualEntities, query_virtual_entities

LEADER = """0
LEADER
5
0
330
0
100
AcDbEntity
8
0
100
AcDbLeader
3
DIMSTYLE
73
3
40
1.0
41
1.0
76
3
10
0.0
20
0.0
30
0.0
10
0.0
20
0.0
30
0.0
10
0.0
20
0.0
30
0.0
340
FEFE
210
0.0
220
0.0
230
1.0
213
0.0
223
0.0
233
0.0
"""


@pytest.fixture
def entity():
    return Leader.from_text(LEADER)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert "LEADER" in ENTITY_CLASSES


def test_default_init():
    entity = Leader()
    assert entity.dxftype() == "LEADER"
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Leader.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": 7,
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.dimstyle == "Standard"
    assert entity.dxf.has_arrowhead == 1
    assert entity.dxf.path_type == 0
    assert entity.dxf.annotation_type == 3
    assert entity.dxf.hookline_direction == 1
    assert entity.dxf.has_hookline == 1
    assert entity.dxf.text_height == 1
    assert entity.dxf.text_width == 1
    assert entity.dxf.block_color == 7
    assert entity.dxf.annotation_handle == "0"
    assert entity.dxf.normal_vector == (0, 0, 1)
    assert entity.dxf.horizontal_direction == (1, 0, 0)
    assert entity.dxf.leader_offset_block_ref == (0, 0, 0)
    assert entity.dxf.leader_offset_annotation_placement == (0, 0, 0)
    assert len(entity.vertices) == 0


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 256, "default color is 256 (by layer)"
    assert entity.dxf.dimstyle == "DIMSTYLE"
    assert entity.dxf.has_arrowhead == 1
    assert entity.dxf.path_type == 0
    assert entity.dxf.annotation_type == 3
    assert entity.dxf.hookline_direction == 1
    assert entity.dxf.has_hookline == 1
    assert entity.dxf.text_height == 1
    assert entity.dxf.text_width == 1
    assert entity.dxf.block_color == 7
    assert entity.dxf.annotation_handle == "FEFE"
    assert entity.dxf.normal_vector == (0, 0, 1)
    assert entity.dxf.horizontal_direction == (1, 0, 0)
    assert entity.dxf.leader_offset_block_ref == (0, 0, 0)
    assert entity.dxf.leader_offset_annotation_placement == (0, 0, 0)
    assert len(entity.vertices) == 3


def test_write_dxf():
    entity = Leader.from_text(LEADER)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(LEADER)
    assert result == expected


VERTICES = [
    (0, 0, 0),
    (1, 1, 0),
    (2, 1, 0),
]


def test_add_leader():
    msp = VirtualLayout()
    leader = msp.add_leader(vertices=VERTICES)
    assert leader.dxftype() == "LEADER"
    assert leader.dxf.annotation_type == 3
    assert len(leader.vertices) == 3
    assert leader.vertices == VERTICES


def test_supports_virtual_entities_protocol():
    leader = Leader.new()
    leader.vertices = VERTICES
    assert isinstance(leader, SupportsVirtualEntities)
    assert len(query_virtual_entities(leader)) == 2
