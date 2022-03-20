#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import Vec2, UCS, NULLVEC, ConstructionBox
from ezdxf.render import forms, mleader

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()


def quick_mtext_horizontal(filename: str):
    doc = ezdxf.new(setup=True)
    # Create a new custom MLEADERSTYLE:
    mleaderstyle = doc.mleader_styles.duplicate_entry("Standard", "EZDXF")
    # The required TEXT style "OpenSans" was created by ezdxf.new() because setup is True:
    mleaderstyle.set_mtext_style("OpenSans")
    msp = doc.modelspace()
    target_point = Vec2(40, 15)
    msp.add_circle(
        target_point, radius=0.5, dxfattribs=GfxAttribs(color=colors.RED)
    )

    for angle in [45, 135, 225, -45]:
        ml_builder = msp.add_multileader_mtext("EZDXF")
        ml_builder.quick_leader(
            f"angle={angle}°\n2nd text line",
            target=target_point,
            segment1=Vec2.from_deg_angle(angle, 14),
        )

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / filename)


def quick_mtext_vertical(filename: str):
    doc = ezdxf.new(setup=True)
    mleaderstyle = doc.mleader_styles.duplicate_entry("Standard", "EZDXF")
    mleaderstyle.set_mtext_style("OpenSans")
    mleaderstyle.dxf.char_height = 2.0  # set the default char height of MTEXT
    msp = doc.modelspace()
    target_point = Vec2(40, 15)
    msp.add_circle(
        target_point, radius=0.5, dxfattribs=GfxAttribs(color=colors.RED)
    )

    for angle in [45, 135, 225, -45]:
        ml_builder = msp.add_multileader_mtext("EZDXF")
        ml_builder.quick_leader(
            f"angle={angle}°\n2nd text line",
            target=target_point,
            segment1=Vec2.from_deg_angle(angle, 14),
            connection_type=mleader.VerticalConnection.center_overline,
        )

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / filename)


if __name__ == '__main__':
    quick_mtext_horizontal("quick_mtext_horizontal.dxf")
    quick_mtext_vertical("quick_mtext_vertical.dxf")