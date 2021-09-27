# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.lldxf.const import versions_supported_by_new

DIR = pathlib.Path("~/Desktop/Outbox").expanduser()


def create_doc(dxfversion):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    msp.add_circle(
        center=(0, 0),
        radius=1.5,
        dxfattribs={
            "layer": "test",
            "linetype": "DASHED",
        },
    )

    zoom.extents(msp, factor=1.1)
    filename = DIR / f"{doc.acad_release}.dxf"
    doc.saveas(filename)
    print("drawing '%s' created.\n" % filename)


if __name__ == "__main__":
    for version in versions_supported_by_new:
        create_doc(version)
