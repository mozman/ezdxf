# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.addons.dxf2code import entities_to_code
from ezdxf.math import Vector  # needed by exec()

doc = ezdxf.new('R2010')
msp = doc.modelspace()


def translate_to_code_and_execute(entity):
    code = entities_to_code([entity], layout='msp').source[0]
    exec(code, globals())
    return msp[-1]


def test_line_to_code():
    from ezdxf.entities.line import Line
    entity = Line.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'start': (1, 2, 3),
        'end': (4, 5, 6),
    })

    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'start', 'end'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_point_to_code():
    from ezdxf.entities.point import Point
    entity = Point.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'location': (1, 2, 3),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'location'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_circle_to_code():
    from ezdxf.entities.circle import Circle
    entity = Circle.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'center': (1, 2, 3),
        'radius': 2,
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'center', 'radius'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_arc_to_code():
    from ezdxf.entities.arc import Arc
    entity = Arc.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'center': (1, 2, 3),
        'radius': 2,
        'start_angle': 30,
        'end_angle': 60,
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'center', 'radius', 'start_angle', 'end_angle'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_text_to_code():
    from ezdxf.entities.text import Text
    entity = Text.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'text': 'xyz',
        'insert': (2, 3, 4),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'text', 'insert'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)
