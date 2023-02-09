# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import dimstyles, LinearDimension, AngularDimension
from ezdxf.addons import ArcDimension, RadialDimension

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# These add-ons are obsolete since the rendering of DIMENSION entities is
# supported by ezdxf but these add-ons will be preserved as they are!
# ------------------------------------------------------------------------------

# create a new drawing: dxfwrite.DXFEngine.drawing(filename)
NAME = "dimlines.dxf"
doc = ezdxf.new("R12")
msp = doc.modelspace()


def render(dimline):
    dimline.render(msp)


# add block and layer definition to drawing
dimstyles.setup(doc)

# create a dimension line for following points
points = [(1.7, 2.5), (0, 0), (3.3, 6.9), (8, 12)]

# define new dimstyles, for predefined ticks see dimlines.py
dimstyles.new("dots", tick="DIMTICK_DOT", scale=1.0, roundval=2, textabove=0.5)
dimstyles.new("arrow", tick="DIMTICK_ARROW", tick2x=True, dimlineext=0.0)
dimstyles.new("dots2", tick="DIMTICK_DOT", tickfactor=0.5)


# add linear dimension lines
render(LinearDimension((3, 3), points, dimstyle="dots", angle=15.0))
render(LinearDimension((0, 3), points, angle=90.0))
render(LinearDimension((-2, 14), points, dimstyle="arrow", angle=-10))

# next dimline is added as anonymous block
block = doc.blocks.new_anonymous_block()
msp.add_blockref(block.name, insert=(0, 0), dxfattribs={"layer": "DIMENSIONS"})
dimline = LinearDimension((-2, 3), points, dimstyle="dots2", angle=90.0)
dimline.set_text(1, "CATCH")
dimline.render(block)

# add polyline to drawing
msp.add_polyline2d(points, dxfattribs={"color": 5})

# There are three dimstyle presets for angular dimension
# 'angle.deg' (default), 'angle.rad', 'angle.grad' (gon)
# for deg and grad default roundval = 0
# for rad default roundval = 3

# angular dimension in grad (gon)
render(
    AngularDimension(
        pos=(18, 5),
        center=(15, 0),
        start=(20, 0),
        end=(20, 5),
        dimstyle="angle.grad",
    )
)

# angular dimension in degree (default dimstyle), with one fractional digit
render(
    AngularDimension(
        pos=(18, 10), center=(15, 5), start=(20, 5), end=(20, 10), roundval=1
    )
)
render(
    ArcDimension(
        pos=(23, 5),
        center=(20, 0),
        start=(25, 0),
        end=(25, 5),
        dimstyle="dots2",
    )
)

# RadiusDimension has a special tick
dimstyles.new("radius", height=0.25, prefix="R=")
render(RadialDimension((20, 0), (24, 1.5), dimstyle="radius"))

filepath = CWD / NAME
doc.saveas(filepath)
print(f"drawing '{filepath}' created.")
