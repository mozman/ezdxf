#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import matplotlib.pyplot as plt
import random

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf import bbox
from ezdxf.math import BoundingBox2d

# This example renders the DXF file in 4 tiles including filtering the DXF
# entities outside the rendering area. But the calculation of the bounding boxes
# is also costly and the entities in the overlapping area are rendered multiple
# times, this means this solution takes longer as a single-pass rendering.
# But it shows the concept.

COLORS = list(range(1, 7))
DPI = 300
WIDTH = 400
HEIGHT = 200

doc = ezdxf.new()
msp = doc.modelspace()


def random_points(count):
    for _ in range(count):
        yield WIDTH * random.random(), HEIGHT * random.random()


for s, e in zip(random_points(100), random_points(100)):
    msp.add_line(s, e, dxfattribs={"color": random.choice(COLORS)})

# detecting the drawing extents by ezdxf:
# For big files this can take along time, therefore if you know the extents
# in advance like in this case, use this knowledge!
cache = bbox.Cache()  # reuse calculation for entity filtering
rect = bbox.extents(msp, cache=cache)
WIDTH = rect.size.x
HEIGHT = rect.size.y
LEFT = rect.extmin.x
BOTTOM = rect.extmin.y


VIEWPORT_X = [LEFT, LEFT + WIDTH / 2, LEFT, LEFT + WIDTH / 2]
VIEWPORT_Y = [BOTTOM, BOTTOM, BOTTOM + HEIGHT / 2, BOTTOM + HEIGHT / 2]

ctx = RenderContext(doc)
for quarter in [0, 1, 2, 3]:
    # setup drawing add-on:
    fig = plt.figure(dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    out = MatplotlibBackend(ax)

    # calculate and set render borders:
    left = VIEWPORT_X[quarter]
    bottom = VIEWPORT_Y[quarter]
    ax.set_xlim(left, left + WIDTH / 2)
    ax.set_ylim(bottom, bottom + HEIGHT / 2)

    # set entities outside of the render area invisible:
    # Bounding box calculation can be very costly, especially for deep nested
    # block-references! If you did the extents calculation and reuse the cache
    # you already have paid the price:
    render_area = BoundingBox2d(
        [(left, bottom), (left + WIDTH / 2, bottom + HEIGHT / 2)]
    )

    def is_intersecting_render_area(entity):
        # returns True if entity should be rendered
        entity_bbox = bbox.extents([entity], cache=cache)
        return render_area.has_intersection(entity_bbox)

    # finalizing invokes auto-scaling!
    Frontend(ctx, out).draw_layout(
        msp, finalize=False, filter_func=is_intersecting_render_area
    )

    # set output size in inches
    # width = 6 in x 300 dpi = 1800 px
    # height = 3 in x 300 dpi = 900 px
    fig.set_size_inches(6, 3, forward=True)

    filename = f"lines{quarter}.png"
    print(f'saving to "{filename}"')
    fig.savefig(filename, dpi=DPI)
    plt.close(fig)
