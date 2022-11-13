# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import matplotlib.pyplot as plt

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.math import Vec2
from ezdxf.enums import TextEntityAlignment, MTextEntityAlignment

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to render the modelspace by the drawing add-on and the
# Matplotlib backend to a certain scale.
#
# docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------


def make_doc(offset=(0, 0), size=(3, 4)):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    x, y = offset
    sx, sy = size
    red_dashed = {"color": 1, "linetype": "dashed"}
    msp.add_line((-100, 5), (100, 5), dxfattribs=red_dashed)
    msp.add_line((6, -100), (6, 100), dxfattribs=red_dashed)
    msp.add_lwpolyline(
        [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)], close=True
    )
    center = Vec2(offset) + Vec2(size) * 0.5
    msp.add_text(
        f"{size[0]:.1f} inch x {size[1]:.1f} inch ",
        height=0.25,
        dxfattribs={"style": "OpenSans"},
    ).set_placement(center, align=TextEntityAlignment.MIDDLE_CENTER)
    return doc


def render_limits(
    origin: tuple[float, float],
    size_in_inches: tuple[float, float],
    scale: float,
) -> tuple[float, float, float, float]:
    """Returns the final render limits in drawing units.

    Args:
         origin: lower left corner of the modelspace area to render
         size_in_inches: paper size in inches
         scale: render scale, e.g. scale=100 means 1:100, 1m is
            rendered as 0.01m or 1cm on paper

    """
    min_x, min_y = origin
    max_x = min_x + size_in_inches[0] * scale
    max_y = min_y + size_in_inches[1] * scale
    return min_x, min_y, max_x, max_y


def export_to_scale(
    paper_size: tuple[float, float] = (8.5, 11),
    origin: tuple[float, float] = (0, 0),
    scale: float = 1,
    dpi: int = 300,
):
    """Render the modelspace content with to a specific paper size and scale.

    Args:
        paper_size: paper size in inches
        origin: lower left corner of the modelspace area to render
        scale: render scale, e.g. scale=100 means 1:100, 1m is
            rendered as 0.01m or 1cm on paper
        dpi: pixel density on paper as dots per inch

    """
    doc = make_doc(offset=(1, 2), size=(6.5, 8))
    msp = doc.modelspace()
    msp.add_mtext(
        f"scale = 1:{scale}\n"
        f"paper size = {paper_size[0]:.1f} inch x {paper_size[1]:.1f} inch ",
        dxfattribs={"style": "OpenSans", "char_height": 0.25},
    ).set_location(
        (0.2, 0.2), attachment_point=MTextEntityAlignment.BOTTOM_LEFT
    )

    ctx = RenderContext(doc)
    fig: plt.Figure = plt.figure(dpi=dpi)
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])

    # disable all margins
    ax.margins(0)

    # get the final render limits in drawing units:
    min_x, min_y, max_x, max_y = render_limits(
        origin, paper_size, scale
    )

    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

    out = MatplotlibBackend(ax)
    # finalizing invokes auto-scaling by default!
    Frontend(ctx, out).draw_layout(msp, finalize=False)

    # set output size in inches:
    fig.set_size_inches(paper_size[0], paper_size[1], forward=True)

    fig.savefig(CWD / f"image_scale_1_{scale}.pdf", dpi=dpi)
    plt.close(fig)


if __name__ == "__main__":
    export_to_scale(scale=1)
    export_to_scale(scale=2)
