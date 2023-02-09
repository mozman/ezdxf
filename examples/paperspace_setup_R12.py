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
# setup DXF R12 paperspace layout
#
# The single paperspace layout of DXF R12 is not well-supported, it is preferable
# to use DXF R2000 or later if paperspace layouts are important for your project.
#
# docs about layouts: https://ezdxf.mozman.at/docs/layouts/index.html
# ------------------------------------------------------------------------------

FILENAME = "page_setup_R12.dxf"


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
    # delete '*Active' viewport configuration
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
    viewport.dxf.aspect_ratio = 1.0  # aspect ratio of viewport (x/y)

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


def setup_paperspace(doc: Drawing):
    from ezdxf.layouts import Paperspace

    # DXF R12 supports just one paperspace layout
    layout = cast(Paperspace, doc.layout())
    layout.page_setup(size=(11, 8.5), margins=(1, 2, 1, 2), units="inch")
    lower_left, upper_right = layout.get_paper_limits()
    x1, y1 = lower_left
    x2, y2 = upper_right
    center = lower_left.lerp(upper_right)
    layout.add_line((x1, center.y), (x2, center.y))  # horizontal center line
    layout.add_line((center.x, y1), (center.x, y2))  # vertical center line
    layout.add_circle((0, 0), radius=0.1)  # plot origin


def main():
    doc = ezdxf.new("R12")
    draw_raster(doc)
    setup_active_viewport_configuration(doc)
    setup_paperspace(doc)
    doc.saveas(CWD / FILENAME)
    print(f'DXF file "{FILENAME}" created.')


if __name__ == "__main__":
    main()
