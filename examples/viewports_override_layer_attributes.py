# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.layouts import Paperspace

MESH_SIZE = 20
DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

COUNT = 7
LAYER_NAME = "Layer{}"
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


def original(vp_handle, doc):
    pass


def override_aci(vp_handle, doc):
    for index in range(COUNT):
        layer = doc.layers.get(LAYER_NAME.format(index))
        override = layer.get_vp_overrides()
        override.set_color(vp_handle, index + 1)
        override.commit()


def override_rgb(vp_handle, doc):
    for index in range(COUNT):
        layer = doc.layers.get(LAYER_NAME.format(index))
        override = layer.get_vp_overrides()
        rgb = (100, 20 + 10 * index, 180)
        override.set_rgb(vp_handle, rgb)
        override.commit()


LTYPES = [
    "DASHED2",
    "DOT2",
    "DASHED2",
    "DOT2",
    "DASHED2",
    "DOT2",
    "DASHED2",
    "DOT2",
]


def override_ltype(vp_handle, doc):
    for index in range(COUNT):
        layer = doc.layers.get(LAYER_NAME.format(index))
        override = layer.get_vp_overrides()
        override.set_linetype(vp_handle, LTYPES[index])
        override.commit()


LW = [13, 18, 25, 35, 50, 70, 100, 140]


def override_lw(vp_handle, doc):
    for index in range(COUNT):
        layer = doc.layers.get(LAYER_NAME.format(index))
        override = layer.get_vp_overrides()
        override.set_lineweight(vp_handle, LW[index])
        override.commit()


def create_viewports(paperspace: Paperspace):
    # Define viewports in paper space:
    # center, size=(width, height) defines the viewport in paper space.
    # view_center_point and view_height defines the area in model space
    # which is displayed in the viewport.
    doc = paperspace.doc
    vp_height = 15
    vp_width = 3
    cx = vp_width / 2
    cy = (PAPER_HEIGHT - 2 * MARGIN) / 2
    for func in (
        original,
        override_aci,
        override_rgb,
        override_ltype,
        override_lw,
    ):
        vp = paperspace.add_viewport(
            center=(cx, cy),
            size=(vp_width, vp_height),
            view_center_point=(50, 30),
            view_height=70,
        )
        func(vp.dxf.handle, doc)
        cx += vp_width + MARGIN


def main():
    def make(dxfversion, filename):
        doc = ezdxf.new(dxfversion, setup=True)
        doc.header["$LWDISPLAY"] = 1  # show linewidth in DXF viewer
        msp = doc.modelspace()
        vp_layer = doc.layers.add("VIEWPORTS")
        # switch viewport layer off to hide the viewport border lines
        vp_layer.off()
        for index in range(COUNT):
            doc.layers.add(LAYER_NAME.format(index))
        create_modelspace_content(msp)
        psp: Paperspace = doc.layout("Layout1")  # type: ignore
        psp.page_setup(
            size=(PAPER_WIDTH, PAPER_HEIGHT),
            margins=(MARGIN, MARGIN, MARGIN, MARGIN),
            units="inch",
        )
        create_viewports(psp)
        doc.set_modelspace_vport(60, (50, 30))
        try:
            doc.saveas(DIR / filename)
        except IOError as e:
            print(str(e))

    make("R2000", "viewport_overrides_R2000.dxf")
    make("R2007", "viewport_overrides_R2007.dxf")
    make("R2018", "viewport_overrides_R2018.dxf")


if __name__ == "__main__":
    main()
