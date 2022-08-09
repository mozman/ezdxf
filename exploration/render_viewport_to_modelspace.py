#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import cast
from pathlib import Path
import ezdxf
from ezdxf import colors
from ezdxf.math import Matrix44, ConstructionBox
from ezdxf.layouts import Paperspace, Modelspace
from ezdxf.entities import Viewport

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")


def create_2d_modelspace_content(msp: Modelspace):
    msp.add_polyline2d(
        [(5, 5), (10, 5), (10, 10), (5, 10)],
        close=True,
        dxfattribs={"color": colors.RED},
    )
    msp.add_circle((10, 5), 2.5, dxfattribs={"color": colors.GREEN})
    msp.add_polyline2d(
        [(10, 7.5), (15, 5), (15, 10)],
        close=True,
        dxfattribs={"color": colors.CYAN},
    )


def create_viewports(paperspace: Paperspace):
    # Define viewports in paper space:
    # center, size=(width, height) defines the viewport in paper space.
    # view_center_point and view_height defines the area in model space
    # which is displayed in the viewport.
    txt_attribs = dict(
        style="OpenSans-Bold",
        color=colors.BLUE,
    )
    paperspace.add_viewport(
        center=(2.5, 2.5),
        size=(5, 5),
        view_center_point=(10.0, 7.5),
        view_height=10,
    )
    # scale is calculated by:
    # height of model space (view_height=10) / height of viewport (height=5)
    paperspace.add_text(
        "Scale=1:2", height=0.18, dxfattribs=txt_attribs
    ).set_placement((0, 5.2))

    paperspace.add_viewport(
        center=(8.5, 2.5),
        size=(5, 5),
        view_center_point=(10, 5),
        view_height=25,
    )
    paperspace.add_text(
        "Scale=1:5", height=0.18, dxfattribs=txt_attribs
    ).set_placement((6, 5.2))

    paperspace.add_viewport(
        center=(7.5, 10),
        size=(15, 7.5),
        view_center_point=(10, 6.25),
        view_height=7.5,
    )
    paperspace.add_text(
        "View Scale=1:1", height=0.18, dxfattribs=txt_attribs
    ).set_placement((0, 14))


def make(filename):
    doc = ezdxf.new(setup=True)
    # create/get the default layer for VIEWPORT entities:
    if "VIEWPORTS" not in doc.layers:
        vp_layer = doc.layers.add("VIEWPORTS")
    else:
        vp_layer = doc.layers.get("VIEWPORTS")
    # switch viewport layer off to hide the viewport border lines
    vp_layer.off()
    # the VIEWPORT layer is not fixed:
    # Paperspace.add_viewport(..., dxfattribs={"layer": "MyViewportLayer"})

    create_2d_modelspace_content(doc.modelspace())
    layout = cast(Paperspace, doc.layout("Layout1"))
    layout.page_setup(size=(22, 17), margins=(1, 1, 1, 1), units="inch")
    create_viewports(layout)

    try:
        doc.saveas(CWD / filename)
    except IOError:
        print("Can't write: '%s'" % filename)
    return layout


def get_transformation_matrix(vp: Viewport) -> Matrix44:
    msp_height = vp.dxf.view_height
    vp_height = vp.dxf.height
    scale = vp_height / msp_height
    msp_center_point = vp.dxf.view_center_point
    offset = vp.dxf.center - (msp_center_point * scale)
    return Matrix44.scale(scale) @ Matrix44.translate(offset.x, offset.y, 0)


def render_vp_border(vp: Viewport, msp: Modelspace):
    box = ConstructionBox(vp.dxf.center, vp.dxf.width, vp.dxf.height)
    msp.add_lwpolyline(box.corners, close=True)


def render_viewport(vp: Viewport, msp: Modelspace):
    m = get_transformation_matrix(vp)
    for entity in vp.doc.modelspace():
        render_vp_border(vp, msp)
        copy = entity.copy()
        copy.transform(m)
        msp.add_foreign_entity(copy, copy=False)


def render_psp_in_msp(psp: Paperspace, filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    for viewport in psp.query("VIEWPORT")[1:]:
        # skip the first viewport - defines the paperspace representation in
        # the CAD application
        render_viewport(cast(Viewport, viewport), msp)
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    _layout = make("viewports_in_paperspace.dxf")
    render_psp_in_msp(_layout, "psp2msp.dxf")
