# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from typing import cast
import pathlib
import ezdxf
from ezdxf.layouts import Paperspace


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to freeze layers in VIEWPORT entities.
#
# VIEWPORT: https://ezdxf.mozman.at/docs/dxfentities/viewport.html
# LAYER: https://ezdxf.mozman.at/docs/tables/layer_table_entry.html
# TUTORIAL: https://ezdxf.mozman.at/docs/tutorials/psp_viewports.html
# ------------------------------------------------------------------------------

MESH_SIZE = 20
COUNT = 7
LAYER_NAME = "L{}"
PAPER_WIDTH = 22
PAPER_HEIGHT = 17
MARGIN = 1


def create_modelspace_content(msp):
    x1 = 0
    x2 = 100
    for index in range(COUNT):
        y = index * 10
        layer_name = LAYER_NAME.format(index)
        # color by layer
        # linetype by layer
        # linewidth by layer
        msp.add_line((x1, y), (x2, y), dxfattribs={"layer": layer_name})


def create_viewports(paperspace: Paperspace):
    # Define viewports in paper space:
    # center, size=(width, height) defines the viewport in paperspace.
    # view_center_point and view_height defines the area in modelspace
    # which is displayed in the viewport.
    vp_height = 15
    vp_width = 3
    cx = vp_width / 2
    cy = (PAPER_HEIGHT - 2 * MARGIN) / 2
    for frozen_layers in [
        [],  # no frozen layers
        ["L0", "L1"],
        ["L2", "L3"],
        ["l4", "l5", "l6"],  # case mismatch
        ["undefined"],  # without layer table entry
    ]:
        vp = paperspace.add_viewport(
            center=(cx, cy),
            size=(vp_width, vp_height),
            view_center_point=(50, 30),
            view_height=70,
            status=2,
        )
        vp.frozen_layers = frozen_layers
        cx += vp_width + MARGIN


def main():
    def make(dxfversion):
        doc = ezdxf.new(dxfversion, setup=True)
        msp = doc.modelspace()

        # create the default layer for VIEWPORT entities:
        vp_layer = doc.layers.add("VIEWPORTS")
        # switch viewport layer off to hide the viewport borderlines
        vp_layer.off()
        for index in range(COUNT):
            doc.layers.add(LAYER_NAME.format(index))
        create_modelspace_content(msp)
        psp = cast(Paperspace, doc.layout("Layout1"))
        psp.page_setup(
            size=(PAPER_WIDTH, PAPER_HEIGHT),
            margins=(MARGIN, MARGIN, MARGIN, MARGIN),
            units="inch",
        )
        create_viewports(psp)
        doc.set_modelspace_vport(60, (50, 30))
        filename = f"viewport_frozen_layers_{dxfversion}.dxf"
        try:
            doc.saveas(CWD / filename)
        except IOError as e:
            print(str(e))

    make("R2000")
    make("R2007")
    make("R2018")


if __name__ == "__main__":
    main()
