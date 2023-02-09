#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import List
import pytest
import ezdxf
from ezdxf.disassemble import recursive_decompose
from ezdxf.entities import Point, Insert


@pytest.fixture(scope="module")
def doc():
    d = ezdxf.new()
    l0 = d.blocks.new("L0")
    build_level_0(l0)
    l1 = d.blocks.new("L1")
    build_nesting_level_1(l1)
    return d


def build_level_0(l0):
    # Block of 4 lines in 4 different colors
    l0.add_line((1, -1), (1, 1), dxfattribs={"color": 1})
    l0.add_line((1, 1), (-1, 1), dxfattribs={"color": 2})
    l0.add_line((-1, 1), (-1, -1), dxfattribs={"color": 3})
    l0.add_line((-1, -1), (1, -1), dxfattribs={"color": 4})


def scale(sx, sy, sz):
    return {
        "xscale": sx,
        "yscale": sy,
        "zscale": sz,
    }


def build_nesting_level_1(l1, name="L0"):
    l1.add_blockref(name, (0, 0), dxfattribs=scale(1, 1, 1))
    l1.add_blockref(name, (3, 0), dxfattribs=scale(-1, 1, 1))
    l1.add_blockref(name, (6, 0), dxfattribs=scale(1, -1, 1))
    l1.add_blockref(name, (9, 0), dxfattribs=scale(-1, -1, 1))
    l1.add_blockref(name, (0, 3), dxfattribs=scale(1, 1, -1))
    l1.add_blockref(name, (3, 3), dxfattribs=scale(-1, 1, -1))
    l1.add_blockref(name, (6, 3), dxfattribs=scale(1, -1, -1))
    l1.add_blockref(name, (9, 3), dxfattribs=scale(-1, -1, -1))


def count(doc, block_names) -> int:
    count = 1
    for name in block_names:
        block = doc.blocks.get(name)
        count *= len(block)
    return count


def test_decompose_block_level_0(doc):
    l0 = doc.blocks.get("L0")
    result = list(recursive_decompose(l0))
    assert len(result) == count(doc, ["L0"])


REFLECTIONS = [(1, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, -1)]
NAMES = [
    "normal",
    "reflect-x",
    "reflect-y",
    "reflect-z",
]


@pytest.mark.parametrize("sx,sy,sz", REFLECTIONS, ids=NAMES)
def test_decompose_block_reference_level_0(doc, sx, sy, sz):
    msp = doc.modelspace()
    msp.delete_all_entities()
    msp.add_blockref("L0", (0, 0), dxfattribs=scale(sx, sy, sz))
    result = list(recursive_decompose(msp))
    assert len(result) == count(doc, ["L0"])


def test_decompose_block_level_1(doc):
    l1 = doc.blocks.get("L1")
    types = [e.dxftype() for e in recursive_decompose(l1)]
    assert len(types) == count(doc, ["L0", "L1"])
    assert set(types) == {"LINE"}, "expected only LINES"


@pytest.mark.parametrize("sx,sy,sz", REFLECTIONS, ids=NAMES)
def test_decompose_block_reference_level_1(doc, sx, sy, sz):
    msp = doc.modelspace()
    msp.delete_all_entities()
    msp.add_blockref("L1", (0, 0), dxfattribs=scale(sx, sy, sz))
    types = [e.dxftype() for e in recursive_decompose(msp)]
    assert len(types) == count(doc, ["L0", "L1"])
    assert set(types) == {"LINE"}, "expected only LINES"


def test_decompose_minsert_level_1(doc):
    nrows = 2
    ncols = 2
    expected_count = count(doc, ["L0", "L1"]) * nrows * ncols

    msp = doc.modelspace()
    msp.delete_all_entities()
    msp.add_blockref(
        "L1",
        (0, 0),
        dxfattribs={
            "row_count": nrows,
            "row_spacing": 5,
            "column_count": ncols,
            "column_spacing": 5,
        },
    )
    types = [e.dxftype() for e in recursive_decompose(msp)]
    assert len(types) == expected_count
    assert set(types) == {"LINE"}, "expected only LINES"


class TestSourceBlockReferences:
    @pytest.fixture(scope="class")
    def doc(self):
        doc_ = ezdxf.new()
        blk0 = doc_.blocks.new("BLK0")
        blk1 = doc_.blocks.new("BLK1")
        blk2 = doc_.blocks.new("BLK2")

        blk2.add_point((2, 1))
        blk2.add_point((2, 2))
        blk1.add_point((1, 1))
        blk1.add_point((1, 2))
        # block reference 2
        blk1.add_blockref("BLK2", (2, 2))
        blk0.add_point((0, 1))
        blk0.add_point((0, 2))
        # block reference 1
        blk0.add_blockref("BLK1", (1, 1))
        # block reference 0
        doc_.modelspace().add_blockref("BLK0", (0, 0))
        return doc_

    @pytest.fixture(scope="class")
    def entities(self, doc):
        return list(recursive_decompose(doc.modelspace()))

    def test_count_of_expected_virtual_entities(self, entities: List[Point]):
        """The virtual INSERT entities are not returned by the
        recursive_decompose() function.
        """
        assert len(entities) == 6, "expected only 6 POINT entities"

    def test_same_source_block_references_blk0(self, entities):
        """Entities from the same INSERT entity have the same virtual source
        block reference.
        """
        insert0 = entities[0].source_block_reference
        insert1 = entities[1].source_block_reference
        assert isinstance(insert0, Insert)
        assert insert0 is insert1
        assert insert0.dxf.name == "BLK0"

    def test_same_source_block_references_blk1(self, entities):
        """Entities from the same INSERT entity have the same virtual source
        block reference.
        """
        insert0 = entities[2].source_block_reference
        insert1 = entities[3].source_block_reference
        assert insert0 is insert1
        assert insert0.dxf.name == "BLK1"

    def test_same_source_block_references_blk2(self, entities):
        """Entities from the same INSERT entity have the same virtual source
        block reference.
        """
        insert0 = entities[4].source_block_reference
        insert1 = entities[5].source_block_reference
        assert insert0 is insert1
        assert insert0.dxf.name == "BLK2"

    def test_link_structure_of_virtual_block_references(self, entities):
        """It is possible to trace back the nesting structure of the block
        references by the source_block_reference property of the virtual
        INSERT entities.
        """
        blkref0 = entities[0].source_block_reference
        blkref1 = entities[2].source_block_reference
        blkref2 = entities[4].source_block_reference
        # blkref2 resides in blkref1
        assert blkref2.source_block_reference is blkref1
        # and blkref1 resides in blkref0
        assert blkref1.source_block_reference is blkref0
        # and blkref0 has no source_block_reference
        assert blkref0.source_block_reference is None


if __name__ == "__main__":
    pytest.main([__file__])
