# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
from typing import cast
import pathlib
import ezdxf
from ezdxf.document import Drawing

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# setup DXF R2000 paperspace layout
#
# For most use cases a paperspace scaling of 1:1 is to prefer and important:
# the paperspace scaling has no influence on the VIEWPORT scaling - this is a
# total different topic, see example "viewports_in_paperspace.py"
# ------------------------------------------------------------------------------

FILENAME = "page_setup_R2000.dxf"


def draw_raster(doc: Drawing):
    marker = doc.blocks.new(name="MARKER")
    attribs = {"color": 2}
    marker.add_line((-1, 0), (1, 0), dxfattribs=attribs)
    marker.add_line((0, -1), (0, 1), dxfattribs=attribs)
    marker.add_circle((0, 0), 0.4, dxfattribs=attribs)

    marker.add_attdef(
        "XPOS", (0.5, -1.0), dxfattribs={"height": 0.25, "color": 4}
    )
    marker.add_attdef(
        "YPOS", (0.5, -1.5), dxfattribs={"height": 0.25, "color": 4}
    )
    modelspace = doc.modelspace()
    for x in range(10):
        for y in range(10):
            xcoord = x * 10
            ycoord = y * 10
            values = {
                "XPOS": f"x = {xcoord}",
                "YPOS": f"y = {ycoord}",
            }
            modelspace.add_auto_blockref("MARKER", (xcoord, ycoord), values)


def setup_active_viewport_configuration(doc: Drawing):
    # This creates a multi-window configuration for the modelspace.
    #
    # delete the current '*Active' viewport configuration
    doc.viewports.delete_config("*ACTIVE")
    # the available display area in AutoCAD has the virtual lower-left
    # corner (0, 0) and the virtual upper-right corner (1, 1)

    # first viewport, uses the left half of the screen
    viewport = doc.viewports.new("*ACTIVE")
    viewport.dxf.lower_left = (0, 0)
    viewport.dxf.upper_right = (0.5, 1)

    # target point defines the origin of the DCS, this is the default value
    viewport.dxf.target = (0, 0, 0)

    # move this location (in DCS) to the center of the viewport
    viewport.dxf.center = (40, 30)

    # height of viewport in drawing units, this parameter works
    viewport.dxf.height = 15

    # aspect ratio of viewport (x/y)
    viewport.dxf.aspect_ratio = 1.0

    # second viewport, uses the right half of the screen
    viewport = doc.viewports.new("*ACTIVE")
    viewport.dxf.lower_left = (0.5, 0)
    viewport.dxf.upper_right = (1, 1)

    # target point defines the origin of the DCS
    viewport.dxf.target = (60, 20, 0)

    # move this location (in DCS, model space = 60, 20) to the center of the viewport
    viewport.dxf.center = (0, 0)

    # height of viewport in drawing units, this parameter works
    viewport.dxf.height = 15

    # aspect ratio of viewport (x/y)
    viewport.dxf.aspect_ratio = 2.0


def setup_paperspace_layouts(doc: Drawing):
    setup_layout1(doc)
    setup_layout2(doc)
    setup_layout3(doc)
    setup_layout4(doc)


def setup_layout1(doc: Drawing):
    from ezdxf.layouts import Paperspace

    name = "Layout1"
    if name in doc.layouts:
        layout = cast(Paperspace, doc.layouts.get(name))
    else:
        layout = doc.layouts.new(name)

    layout.page_setup(
        size=(11, 8.5), margins=(0.5, 0.5, 0.5, 0.5), units="inch"
    )
    lower_left, upper_right = layout.get_paper_limits()
    x1, y1 = lower_left
    x2, y2 = upper_right
    center = lower_left.lerp(upper_right)

    # Add DXF entities to the "Layout1" in paperspace coordinates:
    layout.add_line((x1, center.y), (x2, center.y))  # horizontal center line
    layout.add_line((center.x, y1), (center.x, y2))  # vertical center line
    layout.add_circle((0, 0), radius=0.1)  # plot origin


def setup_layout2(doc: Drawing):
    layout2 = doc.layouts.new("scale 1-1")
    # The default paperspace scale is 1:1
    # 1 mm printed is 1 drawing unit in paperspace
    # For most use cases this is the preferred scaling and important fact:
    # the paperspace scaling has no influence on the VIEWPORT scaling - this is
    # a total different topic, see example "viewports_in_paperspace.py"

    layout2.page_setup(size=(297, 210), margins=(10, 10, 10, 10), units="mm")
    layout2.add_viewport(
        # center of viewport in paperspace units
        center=(100, 100),
        # viewport size in paperspace units
        size=(50, 50),
        # modelspace point to show in center of viewport in WCS
        view_center_point=(60, 40),
        # how much modelspace area to show in viewport in drawing units
        view_height=20,
    )
    lower_left, upper_right = layout2.get_paper_limits()
    x1, y1 = lower_left
    x2, y2 = upper_right
    center = lower_left.lerp(upper_right)

    # Add DXF entities to the "Layout1" in paperspace coordinates:
    layout2.add_line((x1, center.y), (x2, center.y))  # horizontal center line
    layout2.add_line((center.x, y1), (center.x, y2))  # vertical center line
    layout2.add_circle((0, 0), radius=5)  # plot origin


def setup_layout3(doc: Drawing):
    layout3 = doc.layouts.new("scale 1-50")
    # The paperspace is scaled 1:50
    # 1 mm printed is 50 drawing unit in paperspace
    layout3.page_setup(
        size=(297, 210), margins=(10, 10, 10, 10), units="mm", scale=(1, 50)
    )
    layout3.add_viewport(
        # center of viewport in paperspace units, scale = 1:50
        center=(5000, 5000),
        # viewport size in paperspace units, scale = 1:50
        size=(5000, 2500),
        # model space point to show in center of viewport in WCS
        view_center_point=(60, 40),
        # how much model space area to show in viewport in drawing units
        view_height=20,
    )
    layout3.add_circle((0, 0), radius=250)  # plot origin


def setup_layout4(doc: Drawing):
    layout4 = doc.layouts.new("scale 1-1 with offset")
    # The paperspace is scaled 1:1 but has a plot offset
    # 1 mm printed is 1 drawing unit in paperspace

    layout4.page_setup(
        size=(297, 210),
        margins=(10, 10, 10, 10),
        units="mm",
        scale=(1, 1),
        offset=(50, 50),
    )
    lower_left, upper_right = layout4.get_paper_limits()
    x1, y1 = lower_left
    x2, y2 = upper_right
    center = lower_left.lerp(upper_right)

    layout4.add_line((x1, center.y), (x2, center.y))  # horizontal center line
    layout4.add_line((center.x, y1), (center.x, y2))  # vertical center line
    layout4.add_circle((0, 0), radius=5)  # plot origin


def main():
    doc = ezdxf.new("R2000")
    draw_raster(doc)
    setup_active_viewport_configuration(doc)
    setup_paperspace_layouts(doc)
    doc.saveas(CWD / FILENAME)
    print(f'DXF file "{FILENAME}" created.')


if __name__ == "__main__":
    main()
