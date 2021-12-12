#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pathlib
import ezdxf
from ezdxf.math import Vec3, UCS, NULLVEC
import logging
from ezdxf.render.mleader import ConnectionSide

# ========================================
# Setup logging
# ========================================
logging.basicConfig(level="WARNING")

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

DXFVERSION = "R2013"


def simple_mtext_content(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader("Standard")
    ml_builder.set_mtext_content((0, 5), "Line1\nLine2")
    ml_builder.add_leader_line(ConnectionSide.right, vertices=[(10, 10)])
    ml_builder.build()

    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


if __name__ == "__main__":
    simple_mtext_content("simple_mtext")
