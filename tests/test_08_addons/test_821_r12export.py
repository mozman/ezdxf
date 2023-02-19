#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import math

import ezdxf
from ezdxf.addons import r12export
from ezdxf import entities as ents
from ezdxf.render import forms

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


if __name__ == "__main__":
    pytest.main([__file__])
