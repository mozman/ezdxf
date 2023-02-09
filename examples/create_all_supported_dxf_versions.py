# Copyright (c) 2019-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.lldxf.const import versions_supported_by_new
from ezdxf.gfxattribs import GfxAttribs

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# create DXF documents for all supported DXF versions
# ------------------------------------------------------------------------------


def create_doc(dxfversion: str):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    msp.add_circle(
        center=(0, 0),
        radius=1.5,
        dxfattribs=GfxAttribs(layer="test", linetype="DASHED"),
    )

    zoom.extents(msp, factor=1.1)
    filename = CWD / f"{doc.acad_release}.dxf"
    doc.saveas(filename)
    print(f"DXF file '{filename}' created.")


if __name__ == "__main__":
    for version in versions_supported_by_new:
        create_doc(version)
