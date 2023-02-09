# Copyright (c) 2019-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import colors

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows all supported arrow heads.
#
# docs: https://ezdxf.mozman.at/docs/render/arrows.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new("R2007", setup=True)
    msp = doc.modelspace()
    red = {"color": colors.RED}
    white = {"color": colors.WHITE}
    y = 0

    for index, name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
        if name == "":
            label = '"" = closed filled'
        else:
            label = name
        y = index * 2

        def add_connection_point(p):
            msp.add_circle(p, radius=0.01, dxfattribs=red)

        msp.add_text(
            label, dxfattribs={"style": "OpenSans", "height": 0.25}
        ).set_placement((-5, y - 0.5))
        msp.add_line((-5, y), (-1, y))
        msp.add_line((5, y), (10, y))
        # left side |<- is the reverse orientation
        cp1 = msp.add_arrow(
            name, insert=(0, y), size=1, rotation=180, dxfattribs=white
        )
        # right side ->| is the base orientation
        cp2 = msp.add_arrow(
            name, insert=(4, y), size=1, rotation=0, dxfattribs=white
        )
        msp.add_line(cp1, cp2)
        add_connection_point(cp1)
        add_connection_point(cp2)

        add_connection_point(
            msp.add_arrow_blockref(name, insert=(7, y), size=0.3, rotation=45)
        )
        add_connection_point(
            msp.add_arrow_blockref(
                name, insert=(7.5, y), size=0.3, rotation=135
            )
        )
        add_connection_point(
            msp.add_arrow_blockref(name, insert=(8, y), size=0.5, rotation=-90)
        )

    msp.add_line((0, 0), (0, y))
    msp.add_line((4, 0), (4, y))
    msp.add_line((8, 0), (8, y))

    doc.saveas(CWD / f"all_arrows_{doc.acad_release}.dxf")


if __name__ == "__main__":
    main()
