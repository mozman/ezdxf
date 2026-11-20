#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import List
import pytest
import ezdxf
from ezdxf.disassemble import recursive_decompose
from ezdxf.entities import Point, Insert
from ezdxf.math import Vec3


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
    @classmethod
    def doc(cls):
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
    @classmethod
    def entities(cls, doc):
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


def _nested_minsert_doc(outer_attribs):
    doc = ezdxf.new()
    doc.blocks.new("B").add_line((0, 0), (1, 0))
    doc.blocks.new("O").add_blockref("B", (3, 4), dxfattribs={"rotation": 20}).grid(
        size=(2, 2), spacing=(4, 5)
    )
    outer = doc.modelspace().add_blockref("O", (100, 0), dxfattribs=outer_attribs)
    return doc, outer


def _expected_nested_lines(doc, outer):
    minsert = doc.blocks.get("O")[0]
    expected = []
    for cell in minsert.multi_insert():
        matrix = cell.matrix44() @ outer.matrix44()
        expected.append(matrix.transform((0, 0, 0)))
        expected.append(matrix.transform((1, 0, 0)))
    return expected


def _actual_nested_lines(doc):
    points = []
    for entity in recursive_decompose(doc.modelspace()):
        if entity.dxftype() == "LINE":
            points.append(Vec3(entity.dxf.start))
            points.append(Vec3(entity.dxf.end))
    return points


def _assert_same_points(actual, expected):
    def sort_key(point):
        return (round(point.x, 4), round(point.y, 4), round(point.z, 4))

    actual = sorted(actual, key=sort_key)
    expected = sorted(expected, key=sort_key)
    assert len(actual) == len(expected)
    for got, want in zip(actual, expected):
        assert got.isclose(want, abs_tol=1e-6)


@pytest.mark.parametrize(
    "outer_attribs",
    [
        {"rotation": 30},
        {"xscale": 2, "yscale": 2},
        {"xscale": -1, "rotation": 30},
    ],
)
def test_nested_minsert_follows_outer_transform(outer_attribs):
    doc, outer = _nested_minsert_doc(outer_attribs)
    _assert_same_points(_actual_nested_lines(doc), _expected_nested_lines(doc, outer))


def _lines_of_transformed_cells(doc, outer):
    """Where each cell goes when transformed as its own INSERT.

    This is the established non-uniform scaling behaviour of INSERT: grid
    origins follow the matrix, while a rotated insert's content does not match
    a raw non-uniform scale exactly.
    """
    minsert = doc.blocks.get("O")[0]
    points = []
    for cell in minsert.multi_insert():
        clone = cell.copy()
        clone.transform(outer.matrix44())
        matrix = clone.matrix44()
        points.append(matrix.transform((0, 0, 0)))
        points.append(matrix.transform((1, 0, 0)))
    return points


@pytest.mark.parametrize(
    "outer_attribs",
    [
        {"xscale": 2, "yscale": 3},
        {"xscale": 2, "yscale": 3, "rotation": 10},
    ],
)
def test_nested_sheared_minsert_expands_to_single_inserts(outer_attribs):
    doc, outer = _nested_minsert_doc(outer_attribs)
    actual = _actual_nested_lines(doc)
    # One line per grid cell, not just the first cell and not the old spacing.
    assert len(actual) == 8
    _assert_same_points(actual, _lines_of_transformed_cells(doc, outer))
    starts = actual[0::2]
    composed_origins = _expected_nested_lines(doc, outer)[0::2]
    _assert_same_points(starts, composed_origins)


def test_axis_aligned_nested_minsert_keeps_a_grid_under_non_uniform_scale():
    # Unlike a rotated grid, this spacing stays representable. The nested
    # MINSERT is transformed in place rather than expanded.
    doc = ezdxf.new()
    doc.blocks.new("B").add_line((0, 0), (1, 0))
    doc.blocks.new("O").add_blockref("B", (3, 4)).grid(size=(2, 2), spacing=(4, 5))
    doc.modelspace().add_blockref("O", (100, 0), dxfattribs={"xscale": 2, "yscale": 3})
    from ezdxf.explode import virtual_block_reference_entities

    virtual = list(virtual_block_reference_entities(doc.modelspace()[0]))
    assert len(virtual) == 1
    assert virtual[0].dxftype() == "INSERT"
    assert virtual[0].mcount == 4
    assert virtual[0].dxf.row_spacing == pytest.approx(12)
    assert virtual[0].dxf.column_spacing == pytest.approx(10)


if __name__ == "__main__":
    pytest.main([__file__])
