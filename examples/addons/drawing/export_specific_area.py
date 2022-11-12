# Copyright (c) 2020, Matthew Broadway, https://github.com/mozman/ezdxf/discussions/451
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


def draw_raster(msp: Modelspace, x_size: int, y_size: int):
    for x in range(x_size):
        for y in range(y_size):
            text = f"x={x}, y={y}"
            msp.add_text(
                text, height=0.1, dxfattribs=dict(style="Arial")
            ).set_placement((x + 0.1, y + 0.1))
            msp.add_line((x, y), (x + 1, y))
            msp.add_line((x, y), (x, y + 1))


def main():
    # create the DXF document
    doc = ezdxf.new()
    doc.styles.add("Arial", font="arial.ttf")
    msp = doc.modelspace()
    draw_raster(msp, 10, 10)
    doc.set_modelspace_vport(15, center=(5, 5))
    doc.saveas(CWD / "raster.dxf")

    # export the pixel image
    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)

    # setting the export area:
    xmin, xmax = 5, 7
    ymin, ymax = 3, 8
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # set the output size to get the expected aspect ratio:
    fig.set_size_inches(xmax - xmin, ymax - ymin)
    fig.savefig(CWD / "x5y3_to_x7y8.png")


if __name__ == "__main__":
    main()
