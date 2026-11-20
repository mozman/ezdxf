# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import math
from typing import cast
import pytest
import ezdxf
from ezdxf.entities import Insert, Point, Attrib
from ezdxf.entities.insert import ABS_TOL
from ezdxf.math import Matrix44, Vec3, InsertTransformationError


def test_mcount_property():
    insert = Insert.new()
    insert.grid(size=(2, 2), spacing=(10, 10))
    assert insert.mcount == 4

    insert.grid(size=(2, 2), spacing=(10, 0))
    assert insert.mcount == 2

    insert.grid(size=(2, 2), spacing=(0, 10))
    assert insert.mcount == 2

    insert.grid(size=(2, 2), spacing=(0, 0))
    assert insert.mcount == 1


class TestSimpleBlock:
    # without ATTRIB, no rotation, no extrusion
    @pytest.fixture
    def doc(self):
        doc = ezdxf.new()
        blk = doc.blocks.new("POINT")
        blk.add_point(location=(0, 0))
        return doc

    @pytest.fixture
    def insert(self, doc):
        msp = doc.modelspace()
        return msp.add_blockref("POINT", (0, 0))

    @pytest.fixture
    def db(self, doc):
        return doc.entitydb

    def test_minsert_normal_spacing(self, insert):
        insert.grid(size=(2, 2), spacing=(10, 10))
        minsert = list(insert.multi_insert())
        assert len(minsert) == 4
        assert minsert[0].dxf.insert == (0, 0)
        assert minsert[1].dxf.insert == (10, 0)
        assert minsert[2].dxf.insert == (0, 10)
        assert minsert[3].dxf.insert == (10, 10)

    def test_discard_minsert_attribs_from_virtual_insert(self, insert):
        insert.grid(size=(2, 2), spacing=(10, 10))
        vinsert = next(insert.multi_insert())
        assert vinsert.dxf.hasattr("row_count") is False
        assert vinsert.dxf.hasattr("column_count") is False
        assert vinsert.dxf.hasattr("row_spacing") is False
        assert vinsert.dxf.hasattr("column_spacing") is False

    def test_minsert_zero_column_spacing(self, insert):
        insert.grid(size=(2, 2), spacing=(10, 0))
        minsert = list(insert.multi_insert())
        assert len(minsert) == 2
        assert minsert[0].dxf.insert == (0, 0)
        assert minsert[1].dxf.insert == (0, 10)

    def test_minsert_zero_row_spacing(self, insert):
        insert.grid(size=(2, 2), spacing=(0, 10))
        minsert = list(insert.multi_insert())
        assert len(minsert) == 2
        assert minsert[0].dxf.insert == (0, 0)
        assert minsert[1].dxf.insert == (10, 0)

    def test_explode(self, insert, db):
        handle = insert.dxf.handle
        insert.grid(size=(2, 2), spacing=(10, 10))
        points = insert.explode()
        db.purge()

        assert insert.is_alive is False
        assert handle not in db
        assert len(points) == 4
        point = cast(Point, points[3])
        assert point.dxf.owner is not None, "not assigned to a layout"
        assert point.get_layout().name == "Model"
        assert point.dxf.location == (10, 10)


class TestInsertAttributes:
    @pytest.fixture
    def doc(self):
        doc = ezdxf.new()
        blk = doc.blocks.new("POINT")
        blk.add_point(location=(0, 0))
        return doc

    @pytest.fixture
    def insert(self, doc):
        msp = doc.modelspace()
        insert = msp.add_blockref("POINT", (0, 0))
        insert.add_attrib("TEST", text="text", insert=(0, 0))
        return insert

    def test_attribs_transformation(self, insert):
        insert.grid(size=(2, 2), spacing=(10, 10))
        attribs = [i.attribs[0] for i in insert.multi_insert()]

        assert len(attribs) == 4
        assert len(set(id(attrib) for attrib in attribs)) == 4
        assert attribs[0].dxf.insert == (0, 0)
        assert attribs[1].dxf.insert == (10, 0)
        assert attribs[2].dxf.insert == (0, 10)
        assert attribs[3].dxf.insert == (10, 10)

    def test_explode(self, insert, doc):
        db = doc.entitydb
        handle = insert.dxf.handle
        insert.grid(size=(2, 2), spacing=(10, 10))
        entities = insert.explode()
        db.purge()

        assert insert.is_alive is False
        assert handle not in db
        assert len(entities) == 8
        # ATTRIB -> TEXT
        attrib = cast(Attrib, entities.query("TEXT")[3])
        assert attrib.dxf.owner is not None, "not assigned to a layout"
        assert attrib.get_layout().name == "Model"
        assert attrib.dxf.insert == (10, 10)


class TestRotatedInsert:
    angle = 90

    @pytest.fixture
    def insert(self):
        doc = ezdxf.new()
        blk = doc.blocks.new("POINT")
        blk.add_point(location=(0, 0))
        msp = doc.modelspace()

        insert = msp.add_blockref("POINT", (0, 0))
        insert.dxf.rotation = self.angle
        # ATTRIB is placed outside of BLOCK in WCS, INSERT rotation is not
        # applied automatically:
        attrib = insert.add_attrib("TEST", text="text", insert=(0, 0))
        attrib.dxf.rotation = self.angle
        return insert

    def test_minsert_transformation(self, insert):
        insert.grid(size=(2, 2), spacing=(10, 10))
        minsert = list(insert.multi_insert())
        assert len(minsert) == 4
        # Rotated 90° counter clockwise:
        assert minsert[0].dxf.insert.isclose((0, 0))
        assert minsert[1].dxf.insert.isclose((0, 10))
        assert minsert[2].dxf.insert.isclose((-10, 0))
        assert minsert[3].dxf.insert.isclose((-10, 10))

    def test_attribs_transformation(self, insert):
        insert.grid(size=(2, 2), spacing=(10, 10))
        attribs = [i.attribs[0] for i in insert.multi_insert()]
        assert len(attribs) == 4
        assert len(set(id(attrib) for attrib in attribs)) == 4
        # Rotated 90° counter clockwise:
        assert attribs[0].dxf.insert.isclose((0, 0))
        assert attribs[1].dxf.insert.isclose((0, 10))
        assert attribs[2].dxf.insert.isclose((-10, 0))
        assert attribs[3].dxf.insert.isclose((-10, 10))


def _minsert(rotation=0.0, spacing=(4.0, 5.0), size=(2, 2), insert=(3, 4)):
    doc = ezdxf.new()
    doc.blocks.new("B").add_line((0, 0), (1, 0))
    minsert = doc.modelspace().add_blockref(
        "B", insert, dxfattribs={"rotation": rotation}
    )
    minsert.grid(size=size, spacing=spacing)
    return minsert


def _cell_points(minsert):
    """Block origin and a content point of every grid cell, in WCS."""
    points = []
    for cell in minsert.multi_insert():
        matrix = cell.matrix44()
        points.append(matrix.transform((0, 0, 0)))
        points.append(matrix.transform((1, 0, 0)))
    return points


def _assert_same_points(actual, expected):
    def sort_key(point):
        return (round(point.x, 4), round(point.y, 4), round(point.z, 4))

    actual = sorted(actual, key=sort_key)
    expected = sorted(expected, key=sort_key)
    assert len(actual) == len(expected)
    for got, want in zip(actual, expected):
        assert got.isclose(want, abs_tol=1e-6)


# Transformations a MINSERT can still store as row/column spacing.
REPRESENTABLE = [
    ("uniform scale", Matrix44.scale(2, 2, 1), 20),
    ("mirror x", Matrix44.scale(-1, 1, 1), 20),
    ("mirror y", Matrix44.scale(1, -1, 1), 20),
    ("rotate z", Matrix44.z_rotate(math.radians(30)), 20),
    (
        "scale and rotate",
        Matrix44.scale(2, 2, 2) @ Matrix44.z_rotate(math.radians(30)),
        20,
    ),
    ("translate", Matrix44.translate(10, -4, 3), 20),
    ("rotate x", Matrix44.x_rotate(math.radians(90)), 0),
    ("non-uniform axis aligned", Matrix44.scale(2, 3, 1), 0),
    ("negative spacing", Matrix44.scale(2, 2, 1), 15),
    ("extrusion flip", Matrix44.scale(2, 2, -1), 20),
]


@pytest.mark.parametrize(
    "name,matrix,rotation", REPRESENTABLE, ids=[n for n, _, _ in REPRESENTABLE]
)
def test_minsert_transform_moves_grid_with_the_matrix(name, matrix, rotation):
    spacing = (-4, -5) if name == "negative spacing" else (4, 5)
    minsert = _minsert(rotation=rotation, spacing=spacing)
    expected = [matrix.transform(point) for point in _cell_points(minsert)]
    minsert.transform(matrix)
    _assert_same_points(_cell_points(minsert), expected)


def test_uniform_scale_scales_axis_aligned_spacing():
    minsert = _minsert(rotation=0, spacing=(4, 5))
    minsert.transform(Matrix44.scale(2, 3, 1))
    assert minsert.dxf.row_spacing == pytest.approx(12)
    assert minsert.dxf.column_spacing == pytest.approx(10)


def test_non_uniform_scale_of_rotated_grid_raises_and_keeps_entity():
    # Row and column directions are no longer orthogonal after scaling, so the
    # grid can not stay a MINSERT. Leave the entity unchanged.
    minsert = _minsert(rotation=20, spacing=(4, 5))
    before = _cell_points(minsert)
    state = (
        Vec3(minsert.dxf.insert),
        minsert.dxf.rotation,
        minsert.dxf.row_spacing,
        minsert.dxf.column_spacing,
        minsert.dxf.xscale,
        minsert.dxf.yscale,
    )
    with pytest.raises(InsertTransformationError):
        minsert.transform(Matrix44.scale(2, 3, 1))
    assert Vec3(minsert.dxf.insert) == state[0]
    assert minsert.dxf.rotation == state[1]
    assert minsert.dxf.row_spacing == state[2]
    assert minsert.dxf.column_spacing == state[3]
    assert minsert.dxf.xscale == state[4]
    assert minsert.dxf.yscale == state[5]
    _assert_same_points(_cell_points(minsert), before)


def test_non_uniform_scale_of_rotated_rows_only_raises():
    minsert = _minsert(rotation=20, spacing=(4, 5), size=(2, 1))
    with pytest.raises(InsertTransformationError):
        minsert.transform(Matrix44.scale(2, 3, 1))


def test_non_uniform_scale_of_rotated_columns_follows_new_x_axis():
    # The insert rotation is the transformed local x-axis, which is also the
    # column direction, so a columns-only grid stays representable.
    # A non-uniform scaling of a rotated INSERT does not reproduce the content
    # point exactly (existing InsertCoordinateSystem behaviour), so compare the
    # grid origins only. The unused row spacing can not be represented and
    # stays as stored.
    minsert = _minsert(rotation=20, spacing=(4, 5), size=(1, 2))
    matrix = Matrix44.scale(2, 3, 1)
    origins = [cell.matrix44().transform((0, 0, 0)) for cell in minsert.multi_insert()]
    expected = [matrix.transform(point) for point in origins]
    minsert.transform(matrix)
    got = [cell.matrix44().transform((0, 0, 0)) for cell in minsert.multi_insert()]
    _assert_same_points(got, expected)
    assert minsert.dxf.row_spacing == pytest.approx(4)


def test_unused_spacing_follows_an_axis_aligned_scale():
    # column_count is 1, so column spacing places no cells, but it is stored
    # and should still be scaled.
    minsert = _minsert(rotation=0, spacing=(4, 5), size=(2, 1))
    minsert.transform(Matrix44.scale(2, 3, 1))
    assert minsert.dxf.row_spacing == pytest.approx(12)
    assert minsert.dxf.column_spacing == pytest.approx(10)


def test_large_grid_rotation_does_not_raise():
    # A fixed 1e-9 tolerance rejects the float residue of a pure rotation
    # once the spacing reaches about 1e7.
    angles = (1, 20, 33.3, 45, 73, 90, 123.456, 180, 270, 359)
    for angle in angles:
        minsert = _minsert(rotation=15, spacing=(1e7, -1e7))
        matrix = Matrix44.z_rotate(math.radians(angle))
        origins = [
            cell.matrix44().transform((0, 0, 0)) for cell in minsert.multi_insert()
        ]
        expected = [matrix.transform(point) for point in origins]
        minsert.transform(matrix)
        got = [
            cell.matrix44().transform((0, 0, 0)) for cell in minsert.multi_insert()
        ]
        _assert_same_points(got, expected)


def test_large_rotated_grid_still_rejects_non_uniform_scale():
    minsert = _minsert(rotation=20, spacing=(1e7, 1e7))
    with pytest.raises(InsertTransformationError):
        minsert.transform(Matrix44.scale(2, 3, 1))


def test_transform_does_not_invent_spacing_for_a_regular_insert():
    insert = Insert()
    insert.dxf.insert = (0, 0, 0)
    insert.scale(2, 3, 4)
    assert insert.dxf.hasattr("row_spacing") is False
    assert insert.dxf.hasattr("column_spacing") is False


def test_spacing_within_abs_tol_is_left_unchanged():
    # A spacing of magnitude <= ABS_TOL does not place cells. The sign must
    # not matter, and a rotated grid must not raise on a non-uniform scale.
    row_spacing = -ABS_TOL / 10
    column_spacing = ABS_TOL
    minsert = _minsert(rotation=20, spacing=(row_spacing, column_spacing))
    minsert.transform(Matrix44.scale(2, 3, 1))
    assert minsert.dxf.row_spacing == row_spacing
    assert minsert.dxf.column_spacing == column_spacing


def test_spacing_just_above_abs_tol_is_scaled():
    spacing = ABS_TOL * 2
    minsert = _minsert(rotation=0, spacing=(spacing, spacing))
    minsert.transform(Matrix44.scale(2, 3, 1))
    assert minsert.dxf.row_spacing == pytest.approx(spacing * 3)
    assert minsert.dxf.column_spacing == pytest.approx(spacing * 2)


if __name__ == "__main__":
    pytest.main([__file__])
