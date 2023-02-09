# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import pytest
import os
from random import random
import ezdxf
from ezdxf.addons import r12writer

MAX_X_COORD = 1000.0
MAX_Y_COORD = 1000.0
CIRCLE_COUNT = 999


@pytest.fixture(scope="module")
def filename(tmpdir_factory):
    return str(tmpdir_factory.getbasetemp().join("r12writer.dxf"))


def test_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)

    assert not os.path.exists(filename)


def test_write_r12(filename):
    with r12writer(filename) as dxf:
        dxf.add_line((0, 0), (17, 23))
        dxf.add_arc((0, 0), radius=3, start=0, end=175)
        dxf.add_solid([(0, 0), (1, 0), (0, 1), (1, 1)])
        dxf.add_point((1.5, 1.5))
        dxf.add_polyline_2d([(5, 5), (7, 3), (7, 6)])  # 2d polyline
        dxf.add_polyline_2d(
            [(5, 5), (7, 3), (7, 6)], closed=True
        )  # closed 2d polyline
        dxf.add_polyline_2d(
            [(5, 5), (7, 3, 0.5), (7, 6)],
            format="xyb",
            start_width=0.1,
            end_width=0.2,
        )  # 2d polyline with bulge value
        dxf.add_polyline([(4, 3), (8, 5), (2, 4)])  # 2d as 3d polyline
        dxf.add_polyline(
            [(4, 3, 2), (8, 5, 0), (2, 4, 9)], closed=True
        )  # closed 3d polyline
        dxf.add_text("test the text entity", align="MIDDLE_CENTER")

        for i in range(CIRCLE_COUNT):
            dxf.add_circle(
                (MAX_X_COORD * random(), MAX_Y_COORD * random()), radius=2
            )

    assert os.path.exists(filename)


def test_read_r12(filename):
    dwg = ezdxf.readfile(filename)
    msp = dwg.modelspace()
    circles = msp.query("CIRCLE")
    assert len(circles) == CIRCLE_COUNT

    polylines = list(msp.query("POLYLINE"))

    p = polylines[0]  # 2d polyline
    assert len(p) == 3
    assert p.dxf.flags == 0

    p = polylines[1]  # closed 2d polyline
    assert len(p) == 3
    assert p.dxf.flags == 1
    assert p.is_closed is True

    p = polylines[2]  # 2d polyline with bulge value
    assert p.dxf.flags == 0
    assert p.vertices[0].dxf.bulge == 0
    assert p.vertices[1].dxf.bulge == 0.5
    assert p.vertices[2].dxf.bulge == 0
    assert p.dxf.default_start_width == 0.1
    assert p.dxf.default_end_width == 0.2

    p = polylines[3]  # 2d as 3d polyline
    assert len(p) == 3
    assert p.dxf.flags == 8

    p = polylines[4]  # closed 3d polyline
    assert len(p) == 3
    assert p.dxf.flags == 1 + 8
    assert p.is_closed is True


def test_context_manager(filename):
    with pytest.raises(ValueError):
        with r12writer(filename) as dxf:
            dxf.add_line((0, 0), (17, 23))
            raise ValueError()

    dwg = ezdxf.readfile(filename)
    entities = list(dwg.modelspace())
    assert len(entities) == 1
    assert entities[0].dxftype() == "LINE"


def test_write_and_read_binary_dxf(tmpdir_factory):
    filename = str(tmpdir_factory.getbasetemp().join("bin.dxf"))
    with r12writer(filename, fmt="bin") as dxf:
        dxf.add_line((0, 0), (17, 23))

    doc = ezdxf.readfile(filename)
    line = doc.modelspace()[0]
    assert line.dxftype() == "LINE"
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end == (17, 23, 0)

    if os.path.exists(filename):
        os.remove(filename)
