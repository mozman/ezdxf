# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import pytest
import os
from random import random
import ezdxf
from ezdxf.r12writer import r12writer

MAX_X_COORD = 1000.0
MAX_Y_COORD = 1000.0
CIRCLE_COUNT = 999


@pytest.fixture(scope='module')
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
        dxf.add_polyline([(5, 5), (7, 3), (7, 6)])  # 2d polyline
        dxf.add_polyline([(4, 3, 2), (8, 5, 0), (2, 4, 9)])  # 3d polyline
        dxf.add_text("test the text entity", align="MIDDLE_CENTER")

        for i in range(CIRCLE_COUNT):
            dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)

    assert os.path.exists(filename)


def test_read_r12(filename):
    dwg = ezdxf.readfile(filename)
    msp = dwg.modelspace()
    circles = msp.query('CIRCLE')
    assert len(circles) == CIRCLE_COUNT


def test_context_manager(filename):
    with pytest.raises(ValueError):
        with r12writer(filename) as dxf:
            dxf.add_line((0, 0), (17, 23))
            raise ValueError()

    dwg = ezdxf.readfile(filename)
    entities = list(dwg.modelspace())
    assert len(entities) == 1
    assert entities[0].dxftype() == 'LINE'

