# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import matplotlib.pyplot as plt

import ezdxf
from ezdxf.layouts import Modelspace
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def draw_box(msp: Modelspace, width: int, height: int):
    msp.add_lwpolyline(
        [(0, 0), (width, 0), (width, height), (0, height)], close=True
    )
    msp.add_line((0, 0), (width, height))
    msp.add_line((0, height), (width, 0))
    text = f"Box {width}x{height} drawing units"
    msp.add_text(
        text, height=0.1, dxfattribs=dict(style="Arial")
    ).set_placement((0.1, 0.1))


def set_pixel_density(fig: plt.Figure, ax: plt.Axes, ppu: int):
    """Argument `ppu` is pixels per drawing unit."""
    xmin, xmax = ax.get_xlim()
    width = xmax - xmin
    ymin, ymax = ax.get_ylim()
    height = ymax - ymin
    dpi = fig.dpi
    width_inch = width * ppu / dpi
    height_inch = height * ppu / dpi
    fig.set_size_inches(width_inch, height_inch)


def set_pixel_size(fig: plt.Figure, size: tuple[int, int]):
    x, y = size
    fig.set_size_inches(x / fig.dpi, y / fig.dpi)


def main():
    # create the DXF document
    doc = ezdxf.new()
    doc.styles.add("Arial", font="arial.ttf")
    msp = doc.modelspace()
    draw_box(msp, 5, 3)
    doc.set_modelspace_vport(7, center=(2.5, 1.5))
    doc.saveas(CWD / "box.dxf")

    # export the pixel image
    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)

    # set margins as you like (as relative factor of width and height)
    ax.margins(0)

    # export image with 100 pixels per drawing unit = 500x300 pixels
    set_pixel_density(fig, ax, 100)
    fig.savefig(CWD / "box_500x300.png")

    # export image with a size of 1000x600 pixels
    set_pixel_size(fig, (1000, 600))
    fig.savefig(CWD / "box_1000x600.png")

    # add margins and use a different aspect ratio than the modelspace content
    ax.margins(0.01)
    set_pixel_size(fig, (900, 700))
    fig.savefig(CWD / "box_900x700.png")


if __name__ == "__main__":
    main()
