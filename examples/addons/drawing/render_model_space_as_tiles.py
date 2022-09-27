#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterator
import pathlib
import random

import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf import bbox
from ezdxf.math import BoundingBox2d

assert ezdxf.__version__ >= "0.18", "requires ezdxf v0.18b0 or newer"

# ------------------------------------------------------------------------------
# This example renders the DXF file in rows by cols tiles including filtering
# the DXF entities outside the rendering area.
# But the calculation of the bounding boxes is also costly and entities
# expanding into several tiles are rendered multiple times, therefore this
# solution takes longer than a single-pass rendering, but it shows the concept.
#
# docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

COLORS = list(range(1, 7))
DPI = 300
WIDTH = 400
HEIGHT = 200


def random_points(count: int, width: float, height: float):
    for _ in range(count):
        yield width * random.random(), height * random.random()


def create_content(msp):
    for s, e in zip(
        random_points(100, WIDTH, HEIGHT), random_points(100, WIDTH, HEIGHT)
    ):
        msp.add_line(s, e, dxfattribs={"color": random.choice(COLORS)})


def render_areas(extents, grid=(2, 2)) -> Iterator[BoundingBox2d]:
    """Returns a bounding box for each tile to render."""
    rows, cols = grid
    tile_width = extents.size.x / cols
    tile_height = extents.size.y / rows
    for row in range(rows):
        for col in range(cols):
            x_min = extents.extmin.x + col * tile_width
            y_min = extents.extmin.y + row * tile_height
            # BoundingBox2d ignores the z-axis!
            yield BoundingBox2d(
                [(x_min, y_min), (x_min + tile_width, y_min + tile_height)]
            )


def main(rows: int, cols: int):
    doc = ezdxf.new()
    msp = doc.modelspace()
    create_content(msp)

    # Detecting the drawing extents by ezdxf:
    # The bounding box cache can be reused for entity filtering.
    # This cache is a lightweight object, which is compatible to the pickle
    # module, DXF entities are referenced by handle strings. (multiprocessing!)
    cache = bbox.Cache()

    # The bounding box calculation can take a long time for big DXF files!
    # If fast=True the bounding box calculation for curves (SPLINE, ELLIPSE, ...)
    # is based on the control points of the Path class, this is less precise but
    # can speed up the calculation and for this task is a precise bounding box
    # not required.
    # This has no impact on this example which uses only straight lines
    extents = bbox.extents(msp, cache=cache, fast=True)

    ctx = RenderContext(doc)
    for tile, render_area in enumerate(render_areas(extents, (rows, cols))):
        # Setup drawing add-on:
        fig = plt.figure(dpi=DPI)
        ax = fig.add_axes([0, 0, 1, 1])
        out = MatplotlibBackend(ax)

        ax.set_xlim(render_area.extmin.x, render_area.extmax.x)
        ax.set_ylim(render_area.extmin.y, render_area.extmax.y)

        # Disable rendering of entities outside the render area:
        def is_intersecting_render_area(entity):
            """Returns True if entity should be rendered. """
            entity_bbox = bbox.extents([entity], cache=cache, fast=True)
            return render_area.has_intersection(entity_bbox)

        # Finalizing invokes auto-scaling!
        Frontend(ctx, out).draw_layout(
            msp, finalize=False, filter_func=is_intersecting_render_area
        )

        # Set output size in inches:
        # width = 6 inch x 300 dpi = 1800 px
        # height = 3 inch x 300 dpi = 900 px
        fig.set_size_inches(6, 3, forward=True)

        filename = f"tile-{tile:02d}.png"
        print(f'saving tile #{tile} to "{filename}"')
        fig.savefig(CWD / filename, dpi=DPI)
        plt.close(fig)


if __name__ == "__main__":
    main(3, 3)
