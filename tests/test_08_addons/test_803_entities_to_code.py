# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.addons.dxf2code import (
    entities_to_code,
    table_entries_to_code,
    block_to_code,
)
from ezdxf.addons.dxf2code import (
    _fmt_mapping,
    _fmt_list,
    _fmt_api_call,
    _fmt_dxf_tags,
)

from ezdxf.lldxf.types import dxftag
from ezdxf.lldxf.tags import Tags  # required by exec() or eval()
from ezdxf.entities.ltype import LinetypePattern  # required by exec() or eval()

doc = ezdxf.new("R2010")
msp = doc.modelspace()


def test_fmt_mapping():
    from ezdxf.math import Vec3

    d = {"a": 1, "b": "str", "c": Vec3(), "d": "xxx \"yyy\" 'zzz'"}
    r = list(_fmt_mapping(d))
    assert r[0] == "'a': 1,"
    assert r[1] == "'b': \"str\","
    assert r[2] == "'c': (0.0, 0.0, 0.0),"
    assert r[3] == "'d': \"xxx \\\"yyy\\\" 'zzz'\","


def test_fmt_int_list():
    l = [1, 2, 3]
    r = list(_fmt_list(l))
    assert r[0] == "1,"
    assert r[1] == "2,"
    assert r[2] == "3,"


def test_fmt_float_list():
    l = [1.0, 2.0, 3.0]
    r = list(_fmt_list(l))
    assert r[0] == "1.0,"
    assert r[1] == "2.0,"
    assert r[2] == "3.0,"


def test_fmt_vector_list():
    from ezdxf.math import Vec3

    l = [Vec3(), (1.0, 2.0, 3.0)]
    r = list(_fmt_list(l))
    assert r[0] == "(0.0, 0.0, 0.0),"
    assert r[1] == "(1.0, 2.0, 3.0),"


def test_fmt_api_call():
    r = _fmt_api_call(
        "msp.add_line(",
        ["start", "end"],
        dxfattribs={"start": (0, 0), "end": (1, 0), "color": 7},
    )
    assert r[0] == "msp.add_line("
    assert r[1] == "    start=(0, 0),"
    assert r[2] == "    end=(1, 0),"
    assert r[3] == "    dxfattribs={"
    assert r[4] == "        'color': 7,"
    assert r[5] == "    },"
    assert r[6] == ")"


def test_fmt_dxf_tags():
    tags = [dxftag(1, "TEXT"), dxftag(10, (1, 2, 3))]
    code = "[{}]".format("".join(_fmt_dxf_tags(tags)))
    r = eval(code, globals())
    assert r == tags


def translate_to_code_and_execute(entity):
    code = str(entities_to_code([entity], layout="msp"))
    exec(code, globals())
    return msp[-1]


def test_line_to_code():
    from ezdxf.entities.line import Line

    entity = Line.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "start": (1, 2, 3),
            "end": (4, 5, 6),
        },
    )

    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "start", "end"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_point_to_code():
    from ezdxf.entities.point import Point

    entity = Point.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "location": (1, 2, 3),
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "location"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_circle_to_code():
    from ezdxf.entities.circle import Circle

    entity = Circle.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "center": (1, 2, 3),
            "radius": 2,
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "center", "radius"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_arc_to_code():
    from ezdxf.entities.arc import Arc

    entity = Arc.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "center": (1, 2, 3),
            "radius": 2,
            "start_angle": 30,
            "end_angle": 60,
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "center", "radius", "start_angle", "end_angle"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_text_to_code():
    from ezdxf.entities.text import Text

    entity = Text.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "text": "xyz",
            "insert": (2, 3, 4),
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "text", "insert"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_solid_to_code():
    from ezdxf.entities.solid import Solid

    entity = Solid.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "vtx0": (1, 2, 3),
            "vtx1": (4, 5, 6),
            "vtx2": (7, 8, 9),
            "vtx3": (3, 2, 1),
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("vtx0", "vtx1", "vtx2", "vtx3"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_shape_to_code():
    from ezdxf.entities.shape import Shape

    entity = Shape.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "name": "shape_name",
            "insert": (2, 3, 4),
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "name", "insert"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_ellipse_to_code():
    from ezdxf.entities.ellipse import Ellipse

    entity = Ellipse.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "center": (1, 2, 3),
            "major_axis": (2, 0, 0),
            "ratio": 0.5,
            "start_param": 1,
            "end_param": 3,
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in (
        "color",
        "center",
        "major_axis",
        "ratio",
        "start_param",
        "end_param",
    ):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_insert_to_code():
    from ezdxf.entities.insert import Insert

    entity = Insert.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "name": "block1",
            "insert": (2, 3, 4),
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("name", "insert"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_attdef_to_code():
    from ezdxf.entities.attrib import AttDef

    entity = AttDef.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "tag": "TAG1",
            "text": "Text1",
            "insert": (2, 3, 4),
        },
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("tag", "text", "insert"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)


def test_mtext_to_code():
    from ezdxf.entities.mtext import MText

    entity = MText.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "insert": (2, 3, 4),
        },
    )
    text = "xxx \"yyy\" 'zzz'"
    entity.text = text
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "insert"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)
    assert new_entity.text == "xxx \"yyy\" 'zzz'"


def test_lwpolyline_to_code():
    from ezdxf.entities.lwpolyline import LWPolyline

    entity = LWPolyline.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
        },
    )
    entity.set_points(
        [
            (1, 2, 0, 0, 0),
            (4, 3, 0, 0, 0),
            (7, 8, 0, 0, 0),
        ]
    )
    new_entity = translate_to_code_and_execute(entity)
    for name in ("color", "count"):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)
    for np, ep in zip(new_entity.get_points(), entity.get_points()):
        assert np == ep


def test_polyline_to_code():
    # POLYLINE does not work without an entity space
    polyline = msp.add_polyline3d(
        [
            (1, 2, 3),
            (2, 3, 7),
            (9, 3, 1),
            (4, 4, 4),
            (0, 5, 8),
        ]
    )

    new_entity = translate_to_code_and_execute(polyline)
    # Are the last two entities POLYLINE entities?
    assert msp[-2].dxftype() == msp[-1].dxftype()
    assert len(new_entity) == len(polyline)
    assert new_entity.dxf.flags == polyline.dxf.flags
    for np, ep in zip(new_entity.points(), polyline.points()):
        assert np == ep


def test_spline_to_code():
    from ezdxf.entities.spline import Spline

    entity = Spline.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "degree": 3,
        },
    )
    entity.fit_points = [(1, 2, 0), (4, 3, 0), (7, 8, 0)]
    entity.control_points = [(1, 2, 0), (4, 3, 0), (7, 8, 0)]
    entity.knots = [1, 2, 3, 4, 5, 6, 7]
    entity.weights = [1.0, 2.0, 3.0]
    new_entity = translate_to_code_and_execute(entity)
    for name in (
        "color",
        "n_knots",
        "n_control_points",
        "n_fit_points",
        "degree",
    ):
        assert new_entity.get_dxf_attrib(name) == entity.get_dxf_attrib(name)

    assert new_entity.knots == entity.knots
    assert new_entity.control_points.values == entity.control_points.values
    assert new_entity.fit_points.values == entity.fit_points.values
    assert new_entity.weights == entity.weights


def test_leader_to_code():
    from ezdxf.entities.leader import Leader

    entity = Leader.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
        },
    )
    entity.set_vertices(
        [
            (1, 2, 0),
            (4, 3, 0),
            (7, 8, 0),
        ]
    )
    new_entity = translate_to_code_and_execute(entity)
    assert new_entity.dxf.color == entity.dxf.color
    for np, ep in zip(new_entity.vertices, entity.vertices):
        assert np == ep


def test_mesh_to_code():
    from ezdxf.entities.mesh import Mesh
    from ezdxf.render.forms import cube

    entity = Mesh.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
        },
    )
    c = cube()
    entity.vertices = c.vertices
    entity.faces = c.faces

    assert len(entity.vertices) == 8
    new_entity = translate_to_code_and_execute(entity)
    assert list(entity.vertices) == list(new_entity.vertices)
    assert list(entity.faces) == list(new_entity.faces)


def test_layer_entry():
    from ezdxf.entities.layer import Layer

    layer = Layer.new("LAYER", dxfattribs={"name": "TestTest", "color": 3})
    code = table_entries_to_code([layer], drawing="doc")
    exec(str(code), globals())
    layer = doc.layers.get("TestTest")
    assert layer.dxf.color == 3


def test_ltype_entry():
    from ezdxf.entities.ltype import Linetype

    ltype = Linetype.new(
        "FFFF",
        dxfattribs={
            "name": "TEST",
            "description": "TESTDESC",
        },
    )
    ltype.setup_pattern([0.2, 0.1, -0.1])
    code = table_entries_to_code([ltype], drawing="doc")
    exec(str(code), globals())
    new_ltype = doc.linetypes.get("TEST")
    assert new_ltype.dxf.description == ltype.dxf.description
    assert new_ltype.pattern_tags.tags == ltype.pattern_tags.tags
    # all imports added
    assert any(line.endswith("Tags") for line in code.imports)
    assert any(line.endswith("dxftag") for line in code.imports)
    assert any(line.endswith("LinetypePattern") for line in code.imports)


def test_block_to_code():
    testdoc = ezdxf.new()
    block = testdoc.blocks.new("TestBlock", dxfattribs={"description": "test"})
    block.add_line((1, 1), (2, 2))
    code = block_to_code(block, drawing="doc")
    exec(str(code), globals())
    new_block = doc.blocks.get("TestBlock")
    assert new_block.block.dxf.description == block.block.dxf.description
    assert new_block[0].dxftype() == block[0].dxftype()
