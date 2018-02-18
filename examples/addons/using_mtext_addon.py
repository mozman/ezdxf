# Purpose: examples for using MText() add-on
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import MText


def render(mtext):
    mtext.render(msp)


def textblock(text, x, y, rot, color=3, mirror=0):
    attribs = {'color': color}
    msp.add_line((x+50, y), (x+50, y+50),  dxfattribs=attribs)
    msp.add_line((x+100, y), (x+100, y+50), dxfattribs=attribs)
    msp.add_line((x+150, y), (x+150, y+50), dxfattribs=attribs)

    msp.add_line((x+50, y), (x+150, y), dxfattribs=attribs)
    render(MText(text, (x + 50, y), mirror=mirror, rotation=rot))
    render(MText(text, (x + 100, y), mirror=mirror, rotation=rot, align='TOP_CENTER'))
    render(MText(text, (x + 150, y), mirror=mirror, rotation=rot, align='TOP_RIGHT'))

    msp.add_line((x+50, y+25), (x+150, y+25), dxfattribs=attribs)
    render(MText(text, (x + 50, y + 25), mirror=mirror, rotation=rot, align='MIDDLE_LEFT'))
    render(MText(text, (x + 100, y + 25), mirror=mirror, rotation=rot, align='MIDDLE_CENTER'))
    render(MText(text, (x + 150, y + 25), mirror=mirror, rotation=rot, align='MIDDLE_RIGHT'))

    msp.add_line((x+50, y+50), (x+150, y+50), dxfattribs=attribs)
    render(MText(text, (x + 50, y + 50), mirror=mirror, align='BOTTOM_LEFT', rotation=rot))
    render(MText(text, (x + 100, y + 50), mirror=mirror, align='BOTTOM_CENTER', rotation=rot))
    render(MText(text, (x + 150, y + 50), mirror=mirror, align='BOTTOM_RIGHT', rotation=rot))


def rotate_text(text, insert, parts=16, color=3):
    delta = 360. / parts
    for part in range(parts):
        render(MText(text, insert, rotation=(delta*part), color=color, align='TOP_LEFT'))


# MText for DXF R12
dwg = ezdxf.new('R12')
msp = dwg.modelspace()

txt = "Das ist ein mehrzeiliger Text\nZeile 2\nZeile 3\nUnd eine lange lange" \
        " ................ Zeile4"

textblock(txt, 0, 0, 0., color=1)
textblock(txt, 150, 0,  45., color=2)
textblock(txt, 300, 0,  90., color=3)

textblock(txt, 0, 70,  135., color=4)
textblock(txt, 150, 70,  180., color=5)
textblock(txt, 300, 70,  225., color=6)

txt = "MText Zeile 1\nMIRROR_X\nZeile 3"
textblock(txt, 0, 140,  0., color=4, mirror=MText.MIRROR_X)
textblock(txt, 150, 140,  45., color=5, mirror=MText.MIRROR_X)
textblock(txt, 300, 140,  90., color=6, mirror=MText.MIRROR_X)

txt = "MText Zeile 1\nMIRROR_Y\nZeile 3"
textblock(txt, 0, 210,  0., color=4, mirror=MText.MIRROR_Y)
textblock(txt, 150, 210,  45., color=5, mirror=MText.MIRROR_Y)
textblock(txt, 300, 210,  90., color=6, mirror=MText.MIRROR_Y)

textblock("Einzeiler  0 deg", 0, -70, 0., color=1)
textblock("Einzeiler 45 deg", 150, -70,  45., color=2)
textblock("Einzeiler 90 deg", 300, -70,  90., color=3)

txt = "--------------------------------------------------Zeile 1\n" \
      "----------------- MTEXT MTEXT --------------------Zeile 2 zum Rotieren!\n" \
      "--------------------------------------------------Zeile 3\n"
rotate_text(txt, (600, 100), parts=16, color=3)

NAME = "mtext.dxf"
dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
