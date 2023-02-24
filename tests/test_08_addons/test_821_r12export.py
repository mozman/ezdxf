#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import math

import ezdxf
from ezdxf.addons import r12export
from ezdxf import entities as ents
from ezdxf.render import forms
from ezdxf.tools.text import MTextEditor

DXFATTRIBS = {
    "layer": "EZDXF",
    "color": 144,
}


def test_export_empty_doc():
    doc = ezdxf.new("R2018")
    doc_r12 = r12export.convert(doc)
    assert doc_r12.dxfversion == ezdxf.DXF12


def test_export_dxf_primitives():
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    msp.add_point((0, 0))
    msp.add_text("MyText")
    msp.add_line((0, 0), (1, 0))
    msp.add_circle((0, 0), radius=1)
    msp.add_arc((0, 0), radius=1, start_angle=30, end_angle=150)

    doc_r12 = r12export.convert(doc)
    assert len(doc_r12.modelspace()) == len(msp)


def test_export_lwpolyline_as_polyline():
    points = [(0, 0), (1, 0, 0.7), (2, 0), (2, 2)]
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    msp.add_lwpolyline(points, format="xyb", dxfattribs=DXFATTRIBS)

    doc_r12 = r12export.convert(doc)
    polyline: ents.Polyline = doc_r12.modelspace()[0]
    assert isinstance(polyline, ents.Polyline)
    assert polyline.is_2d_polyline is True
    assert len(polyline.vertices) == 4
    assert polyline.vertices[1].dxf.bulge == 0.7
    assert polyline.dxf.layer == "EZDXF"
    assert polyline.dxf.color == 144


def test_export_mesh_as_polyface_mesh():
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    cube = forms.cube()
    cube.render_mesh(msp, dxfattribs=DXFATTRIBS)

    doc_r12 = r12export.convert(doc)
    polyface: ents.Polyface = doc_r12.modelspace()[0]
    assert isinstance(polyface, ents.Polyface)
    assert polyface.is_poly_face_mesh is True
    assert polyface.dxf.layer == "EZDXF"
    assert polyface.dxf.color == 144


def test_export_ellipse_as_3d_polyline():
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    msp.add_ellipse(
        (0, 0), (3, 0), 0.5, start_param=0, end_param=math.pi, dxfattribs=DXFATTRIBS
    )

    doc_r12 = r12export.convert(doc)
    polyline: ents.Polyline = doc_r12.modelspace()[0]
    assert isinstance(polyline, ents.Polyline)
    assert polyline.is_3d_polyline is True
    assert len(polyline.vertices) > 10
    assert polyline.dxf.layer == "EZDXF"
    assert polyline.dxf.color == 144


def test_export_spline_as_3d_polyline():
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    msp.add_spline(fit_points=[(0, 0, 0), (2, 1, 1), (3, 5, -1)], dxfattribs=DXFATTRIBS)

    doc_r12 = r12export.convert(doc)
    polyline: ents.Polyline = doc_r12.modelspace()[0]
    assert isinstance(polyline, ents.Polyline)
    assert polyline.is_3d_polyline is True
    assert len(polyline.vertices) > 10
    assert polyline.dxf.layer == "EZDXF"
    assert polyline.dxf.color == 144


def test_export_proxy_graphic():
    from ezdxf.lldxf.tags import Tags
    from ezdxf.proxygraphic import load_proxy_graphic

    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    proxy_entity = ents.ACADProxyEntity.new()
    proxy_entity.proxy_graphic = load_proxy_graphic(Tags.from_text(DATA))
    msp.add_entity(proxy_entity)

    doc_r12 = r12export.convert(doc)
    insert = doc_r12.modelspace()[0]
    assert insert.dxftype() == "INSERT"
    assert insert.dxf.name == "*U1"

    block = doc_r12.blocks.get(insert.dxf.name)
    assert len(block) == 9


def test_export_mtext():
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    editor = MTextEditor()
    editor.append("LINE0\n")
    editor.font("Arial.ttf")
    editor.append("LINE1")
    msp.add_mtext(editor.text, dxfattribs=DXFATTRIBS)

    doc_r12 = r12export.convert(doc)
    text = doc_r12.modelspace().query("TEXT")
    assert len(text) == 2
    assert doc_r12.styles.has_entry("MTXPL_ARIAL")


DATA = """160
968
310
C80300000D000000540000002000000002000000033E695D8B227240B00D3CF1FB7B5540000000000000000082C85BAC2FDE7240FB1040429FB05740000000000000000000000000000000000000000000000000000000000000F03F5400000020000000020000004AF9442AE7FA60405A2D686189715A4000000000000000
310
00C0DC003571AE5F40043422DDA4515D40000000000000000000000000000000000000000000000000000000000000F03F64000000040000001EA72DF9806A69402CE3B4E7B59D34400000000000000000770FBC9D50855E4000000000000000000000000000000000000000000000F03FB634003D352CE93FB1DDE561C5C1
310
E33F00000000000000000418DC3967E1F83F000000000C0000001200000000000000D0000000260000001F8BC5F8B8B46A40197732241FF06140000000000000000000000000000000000000000000000000000000000000F03F0943D77B25BDEF3F417457E0C451C0BF00000000000000003100370032002C003400320000
310
00000006000000010000000000000000000440000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000000000000000000000000000000000000000000041007200690061006C00000061007200690061006C002E007400740066000000000000000C00000012000000FF7F0000
310
6400000004000000813C33FBB3606A400278BF21B8F4614000000000000000009AEFA7C64B37034000000000000000000000000000000000000000000000F03F0943D77B25BDEF3F437457E0C451C0BF0000000000000000182D4454FB210940000000000C00000010000000010000000C0000001700000000000000540000
310
0020000000020000001EA72DF9806A69402CE3B4E7B59D344000000000000000001EA72DF9806A69402CE3B4E7B59D3440000000000000000000000000000000000000000000000000000000000000F03F540000002000000002000000B296839B8D1A724001000000F06355400000000000000000B296839B8D1A72400100
310
0000F0635540000000000000000000000000000000000000000000000000000000000000F03F540000002000000002000000632D073753076140FFFFFFFF2F525A400000000000000000632D073753076140FFFFFFFF2F525A40000000000000000000000000000000000000000000000000000000000000F03F5400000020
310
000000020000000960E446A3456F405AF2DBF448AB604000000000000000000960E446A3456F405AF2DBF448AB6040000000000000000000000000000000000000000000000000000000000000F03F
"""

if __name__ == "__main__":
    pytest.main([__file__])
