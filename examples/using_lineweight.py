# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use lineweights.
#
# basic concept: https://ezdxf.mozman.at/docs/concepts/lineweights.html
# ------------------------------------------------------------------------------

LAYER_NAME = "Lines"

# line weight im mm times 100, e.g. 0.13mm = 13
# minimum line weight 0
# maximum line width 211
# all valid lineweights are stored in: ezdxf.const.VALID_DXF_LINEWEIGHTS
WEIGHTS = [13, 18, 20, 25, 35, 50, 70, 100, 200, -1, -3]


def lines_with_lineweight(msp, x1, x2):
    for index, lineweight in enumerate(WEIGHTS):
        y = index * 10
        msp.add_line(
            (x1, y),
            (x2, y),
            dxfattribs={
                "layer": LAYER_NAME,
                "lineweight": lineweight,
            },
        )


def lines_with_default_weight(msp, x1, x2):
    for index in range(len(WEIGHTS)):
        y = index * 10
        msp.add_line(
            (x1, y),
            (x2, y),
            dxfattribs={"layer": LAYER_NAME},
        )


doc = ezdxf.new("R2004")
# The CAD application should display lineweights:
doc.header["$LWDISPLAY"] = 1

msp = doc.modelspace()
lines_layer = doc.layers.new(LAYER_NAME)
# set default line width as enum
lines_layer.dxf.lineweight = 35

lines_with_lineweight(msp, x1=0, x2=100)
lines_with_default_weight(msp, x1=150, x2=250)

doc.saveas(CWD / "using_lineweight.dxf")
