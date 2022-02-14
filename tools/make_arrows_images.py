# Copyright (c) 2019-2022, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import colors
from ezdxf.addons.drawing.matplotlib import qsave

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")


def main():
    for name in ezdxf.ARROWS.__all_arrows__:
        make_arrow_image(name)


def make_arrow_image(name):
    def add_connection_point(p):
        msp.add_circle(p, radius=0.01, dxfattribs=red)

    doc = ezdxf.new("R2007", setup=True)
    msp = doc.modelspace()
    red = {"color": colors.RED}
    white = {"color": colors.WHITE}
    y = 0

    if name == "":
        label = '"" = closed filled'
    else:
        label = name

    msp.add_text(
        label, dxfattribs={"style": "OpenSans", "height": 0.25}
    ).set_placement((-5, y - 0.5))
    msp.add_line((-5, y), (-1, y))
    msp.add_line((0, y - 1.0), (0, y + 0.7))  # extension line
    cp1 = msp.add_arrow(
        name, insert=(0, y), size=1, rotation=180, dxfattribs=white
    )
    add_connection_point(cp1)
    qsave(
        msp,
        str(DIR / f"{ezdxf.ARROWS.block_name(name)}.png"),
        bg="#FFFFFF",
        dpi=100,
        size_inches=(3, 1),
    )


if __name__ == "__main__":
    main()
