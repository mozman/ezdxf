# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.addons.dxf2code import entities_to_code

doc = ezdxf.new('R2010')
msp = doc.modelspace()


def translate_to_code_and_execute(entity):
    code = str(entities_to_code([entity], layout='msp'))
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


def test_solid_to_code():
    from ezdxf.entities.solid import Solid
    entity = Solid.new(handle='ABBA', owner='0', dxfattribs={
        'vtx0': (1, 2, 3),
        'vtx1': (4, 5, 6),
        'vtx2': (7, 8, 9),
        'vtx3': (3, 2, 1),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('vtx0', 'vtx1', 'vtx2', 'vtx3'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_shape_to_code():
    from ezdxf.entities.shape import Shape
    entity = Shape.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'name': 'shape_name',
        'insert': (2, 3, 4),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'name', 'insert'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_ellipse_to_code():
    from ezdxf.entities.ellipse import Ellipse
    entity = Ellipse.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'center': (1, 2, 3),
        'major_axis': (2, 0, 0),
        'ratio': .5,
        'start_param': 1,
        'end_param': 3,
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'center', 'major_axis', 'ratio', 'start_param', 'end_param'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_insert_to_code():
    from ezdxf.entities.insert import Insert
    entity = Insert.new(handle='ABBA', owner='0', dxfattribs={
        'name': 'block1',
        'insert': (2, 3, 4),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('name', 'insert'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_attrib_to_code():
    from ezdxf.entities.attrib import Attrib
    entity = Attrib.new(handle='ABBA', owner='0', dxfattribs={
        'tag': 'TAG1',
        'text': 'Text1',
        'insert': (2, 3, 4),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('tag', 'text', 'insert'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_attdef_to_code():
    from ezdxf.entities.attrib import AttDef
    entity = AttDef.new(handle='ABBA', owner='0', dxfattribs={
        'tag': 'TAG1',
        'text': 'Text1',
        'insert': (2, 3, 4),
    })
    new_entity = translate_to_code_and_execute(entity)
    for name in ('tag', 'text', 'insert'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_mtext_to_code():
    from ezdxf.entities.mtext import MText
    entity = MText.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'insert': (2, 3, 4),
    })
    text = 'xxx "yyy" \'zzz\''
    entity.text = text
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'insert'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)
    assert new_entity.text == text


def test_lwpolyline_to_code():
    from ezdxf.entities.lwpolyline import LWPolyline
    entity = LWPolyline.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
    })
    entity.set_points([
        (1, 2, 0, 0, 0),
        (4, 3, 0, 0, 0),
        (7, 8, 0, 0, 0),
    ])
    new_entity = translate_to_code_and_execute(entity)
    for name in ('color', 'count'):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)
    for np, ep in zip(new_entity.get_points(), entity.get_points()):
        assert np == ep


def test_polyline_to_code():
    # POLYLINE does not work without an entity space
    polyline = msp.add_polyline3d([
        (1, 2, 3),
        (2, 3, 7),
        (9, 3, 1),
        (4, 4, 4),
        (0, 5, 8),
    ])

    new_entity = translate_to_code_and_execute(polyline)
    # Are the last two entities POLYLINE entities?
    assert msp[-2].dxftype() == msp[-1].dxftype()
    assert len(new_entity) == len(polyline)
    assert new_entity.dxf.flags == polyline.dxf.flags
    for np, ep in zip(new_entity.points(), polyline.points()):
        assert np == ep


