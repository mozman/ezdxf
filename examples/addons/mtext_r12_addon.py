# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import MText
from ezdxf.math import UVec
from ezdxf.layouts import Modelspace
from ezdxf.enums import MTextEntityAlignment

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# These add-on can be used to create MTEXT like text entities for DXF R12 which
# does not support the MTEXT entity. These add-on can be replaced by exploding
# MTEXT entities by the mtxpl add-on. This add-on will be preserved is it is!
#
# docs: https://ezdxf.mozman.at/docs/addons/mtxpl.html
# ------------------------------------------------------------------------------


def textblock(
    msp: Modelspace,
    text: str,
    x: float,
    y: float,
    rot: float,
    color: int = 3,
    mirror: int = 0,
):
    attribs = {"color": color}
    msp.add_line((x + 50, y), (x + 50, y + 50), dxfattribs=attribs)
    msp.add_line((x + 100, y), (x + 100, y + 50), dxfattribs=attribs)
    msp.add_line((x + 150, y), (x + 150, y + 50), dxfattribs=attribs)

    msp.add_line((x + 50, y), (x + 150, y), dxfattribs=attribs)
    MText(text, (x + 50, y), mirror=mirror, rotation=rot).render(msp)
    MText(
        text,
        (x + 100, y),
        mirror=mirror,
        rotation=rot,
        align=MTextEntityAlignment.TOP_CENTER,
    ).render(msp)
    MText(
        text,
        (x + 150, y),
        mirror=mirror,
        rotation=rot,
        align=MTextEntityAlignment.TOP_RIGHT,
    ).render(msp)

    msp.add_line((x + 50, y + 25), (x + 150, y + 25), dxfattribs=attribs)
    MText(
        text,
        (x + 50, y + 25),
        mirror=mirror,
        rotation=rot,
        align=MTextEntityAlignment.MIDDLE_LEFT,
    ).render(msp)
    MText(
        text,
        (x + 100, y + 25),
        mirror=mirror,
        rotation=rot,
        align=MTextEntityAlignment.MIDDLE_CENTER,
    ).render(msp)

    MText(
        text,
        (x + 150, y + 25),
        mirror=mirror,
        rotation=rot,
        align=MTextEntityAlignment.MIDDLE_RIGHT,
    ).render(msp)

    msp.add_line((x + 50, y + 50), (x + 150, y + 50), dxfattribs=attribs)
    MText(
        text,
        (x + 50, y + 50),
        mirror=mirror,
        align=MTextEntityAlignment.BOTTOM_LEFT,
        rotation=rot,
    ).render(msp)
    MText(
        text,
        (x + 100, y + 50),
        mirror=mirror,
        align=MTextEntityAlignment.BOTTOM_CENTER,
        rotation=rot,
    ).render(msp)
    MText(
        text,
        (x + 150, y + 50),
        mirror=mirror,
        align=MTextEntityAlignment.BOTTOM_RIGHT,
        rotation=rot,
    ).render(msp)


def rotate_text(
    msp: Modelspace, text: str, insert: UVec, parts: int = 16, color: int = 3
):
    delta = 360.0 / parts
    for part in range(parts):
        MText(
            text,
            insert,
            rotation=(delta * part),
            color=color,
            align=MTextEntityAlignment.TOP_LEFT,
        ).render(msp)


def main():
    # MText for DXF R12
    doc = ezdxf.new("R12")
    msp = doc.modelspace()

    txt = (
        "Das ist ein mehrzeiliger Text\nZeile 2\nZeile 3\nUnd eine lange lange"
        " ................ Zeile4"
    )

    textblock(msp, txt, 0, 0, 0.0, color=1)
    textblock(msp, txt, 150, 0, 45.0, color=2)
    textblock(msp, txt, 300, 0, 90.0, color=3)

    textblock(msp, txt, 0, 70, 135.0, color=4)
    textblock(msp, txt, 150, 70, 180.0, color=5)
    textblock(msp, txt, 300, 70, 225.0, color=6)

    txt = "MText Zeile 1\nMIRROR_X\nZeile 3"
    textblock(msp, txt, 0, 140, 0.0, color=4, mirror=MText.MIRROR_X)
    textblock(msp, txt, 150, 140, 45.0, color=5, mirror=MText.MIRROR_X)
    textblock(msp, txt, 300, 140, 90.0, color=6, mirror=MText.MIRROR_X)

    txt = "MText Zeile 1\nMIRROR_Y\nZeile 3"
    textblock(msp, txt, 0, 210, 0.0, color=4, mirror=MText.MIRROR_Y)
    textblock(msp, txt, 150, 210, 45.0, color=5, mirror=MText.MIRROR_Y)
    textblock(msp, txt, 300, 210, 90.0, color=6, mirror=MText.MIRROR_Y)

    textblock(msp, "Einzeiler  0 deg", 0, -70, 0.0, color=1)
    textblock(msp, "Einzeiler 45 deg", 150, -70, 45.0, color=2)
    textblock(msp, "Einzeiler 90 deg", 300, -70, 90.0, color=3)

    txt = (
        "--------------------------------------------------Zeile 1\n"
        "----------------- MTEXT MTEXT --------------------Zeile 2 zum Rotieren!\n"
        "--------------------------------------------------Zeile 3\n"
    )
    rotate_text(msp, txt, (600, 100), parts=16, color=3)

    filepath = CWD / "mtext_r12.dxf"
    doc.saveas(filepath)
    print(f"drawing '{filepath}' created.\n")


if __name__ == "__main__":
    main()
