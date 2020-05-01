# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import random

import pytest
import math

from ezdxf.explode import angle_to_param
from ezdxf.math import Vector
from ezdxf.entities.ellipse import Ellipse
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

ELLIPSE = """0
ELLIPSE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbEllipse
10
0.0
20
0.0
30
0.0
11
1.0
21
0.0
31
0.0
40
1.0
41
0.0
42
6.283185307179586
"""


@pytest.fixture
def entity():
    return Ellipse.from_text(ELLIPSE)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'ELLIPSE' in ENTITY_CLASSES


def test_default_init():
    entity = Ellipse()
    assert entity.dxftype() == 'ELLIPSE'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Ellipse.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'ratio': 2,
        'center': (1, 2, 3),
        'major_axis': (4, 5, 6),
        'start_param': 10,
        'end_param': 20,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.center == (1, 2, 3)
    assert entity.dxf.major_axis == (4, 5, 6)
    assert entity.dxf.ratio == 2
    assert entity.dxf.start_param == 10
    assert entity.dxf.end_param == 20


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.center == (0, 0, 0)
    assert entity.dxf.major_axis == (1, 0, 0)
    assert entity.dxf.ratio == 1
    assert entity.dxf.start_param == 0
    assert entity.dxf.end_param == math.pi * 2


def test_get_start_and_end_vertex():
    ellipse = Ellipse.new(handle='ABBA', owner='0', dxfattribs={
        'center': (1, 2, 3),
        'major_axis': (4, 3, 0),
        'ratio': .7,
        'start_param': math.pi / 2,
        'end_param': math.pi,
        'extrusion': (0, 0, -1),
    })

    start, end = list(ellipse.vertices([
        ellipse.dxf.start_param,
        ellipse.dxf.end_param,
    ]))
    # test values from BricsCAD
    assert start.isclose(Vector(3.1, -0.8, 3), abs_tol=1e-6)
    assert end.isclose(Vector(-3, -1, 3), abs_tol=1e-6)

    # for convenience, but Ellipse.vertices is much more efficient:
    assert ellipse.start_point.isclose(Vector(3.1, -0.8, 3), abs_tol=1e-6)
    assert ellipse.end_point.isclose(Vector(-3, -1, 3), abs_tol=1e-6)


def test_write_dxf():
    entity = Ellipse.from_text(ELLIPSE)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(ELLIPSE)
    assert result == expected


def test_from_arc():
    from ezdxf.entities.arc import Arc
    arc = Arc.new(dxfattribs={'center': (2, 2, 2), 'radius': 3})
    ellipse = Ellipse.from_arc(arc)
    assert ellipse.dxf.center == (2, 2, 2)
    assert ellipse.dxf.major_axis == (3, 0, 0)
    assert ellipse.dxf.ratio == 1
    assert ellipse.dxf.start_param == 0
    assert math.isclose(ellipse.dxf.end_param, math.pi * 2)


def test_swap_axis_full_ellipse():
    ellipse = Ellipse.new(dxfattribs={
        'major_axis': (5, 0, 0),
        'ratio': 2,  # > 1 is not valid
    })
    assert ellipse.minor_axis.isclose((0, 10, 0))

    ellipse.swap_axis()
    assert ellipse.dxf.ratio == 0.5
    assert ellipse.dxf.major_axis == (0, 10, 0)
    assert ellipse.minor_axis == (-5, 0, 0)
    assert ellipse.dxf.start_param == 0
    assert ellipse.dxf.end_param == math.pi * 2


def test_swap_axis_half_ellipse():
    ellipse = Ellipse.new(dxfattribs={
        'major_axis': (5, 0, 0),
        'ratio': 2,  # > 1 is not valid
        'start_param': math.pi / 2.0,
        'end_param': math.pi / 2.0 * 3.0
    })
    assert ellipse.minor_axis.isclose((0, 10, 0))

    ellipse.swap_axis()
    assert ellipse.dxf.ratio == 0.5
    assert ellipse.dxf.major_axis == (0, 10, 0)
    assert ellipse.minor_axis == (-5, 0, 0)
    assert ellipse.dxf.start_param == 0
    assert ellipse.dxf.end_param == math.pi


def test_swap_axis_arbitrary_params():
    def random_params(count):
        return [random.random() * math.tau for _ in range(count)]

    for start_param, end_parm in zip(random_params(10), random_params(10)):
        ellipse = Ellipse.new(dxfattribs={
            'major_axis': (5, 0, 0),
            'ratio': 2,  # > 1 is not valid
            'start_param': start_param,
            'end_param': end_parm
        })
        start_point = ellipse.start_point
        end_point = ellipse.end_point

        ellipse.swap_axis()
        assert ellipse.dxf.ratio == 0.5
        assert ellipse.start_point.isclose(start_point, abs_tol=1e-9)
        assert ellipse.end_point.isclose(end_point, abs_tol=1e-9)


def test_angle_to_param():
    angle = 1.23
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = 1.23 + math.pi / 2
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = 1.23 + math.pi
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = 1.23 + 3 * math.pi / 2
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = math.pi / 2 + 1e-15
    assert math.isclose(angle_to_param(1.0, angle), angle)

    random.seed(0)
    for i in range(1000):
        ratio = random.uniform(0, 1)
        angle = random.uniform(0, math.tau)
        param = angle_to_param(ratio, angle)
        ellipse = Ellipse.new(dxfattribs={
            'major_axis': (random.uniform(-10, 10), random.uniform(-10, 10), 0),
            'ratio': ratio,
            'start_param': 0,
            'end_param': param,
            'extrusion': (0, 0, random.choice([1, -1])),
        })
        calculated_angle = ellipse.dxf.extrusion.angle_about(ellipse.dxf.major_axis, ellipse.end_point)
        calculated_angle_without_direction = ellipse.dxf.major_axis.angle_between(ellipse.end_point)
        assert math.isclose(calculated_angle, angle, abs_tol=1e-5)
        assert (math.isclose(calculated_angle, calculated_angle_without_direction) or
                math.isclose(math.tau - calculated_angle, calculated_angle_without_direction))
