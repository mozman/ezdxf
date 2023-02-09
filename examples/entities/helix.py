#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import math
import ezdxf

from ezdxf.math import Matrix44

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

# ------------------------------------------------------------------------------
# this example shows how to create a HELIX entity.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/helix.html
# ------------------------------------------------------------------------------


def simple_helix(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_helix(radius=5, pitch=1, turns=5)
    doc.saveas(CWD / filename)


def transform_helix(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    helix = msp.add_helix(radius=5, pitch=1, turns=5)
    helix.transform(Matrix44.x_rotate(math.pi/4) @ Matrix44.translate(2, 4, 6))
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    simple_helix("simple_helix.dxf")
    transform_helix("transform_helix.dxf")
