# Copyright (c) 2021 Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.tools.text import MTextEditor

OUTBOX = Path('~/Desktop/Outbox').expanduser()
ATTRIBS = {
    'char_height': 0.7,
    'style': 'OpenSans',
}

# use constants defined in MTextEditor:
NP = MTextEditor.NEW_PARAGRAPH


def recreate_mtext_py_example(msp, location):
    # replicate example "mtext.py":
    attribs = dict(ATTRIBS)
    attribs['width'] = 15.0
    editor = MTextEditor(f"recreate mtext.py result:{NP}normal ").overline(
        "over line").append(" normal" + NP + "normal ").strike_through(
        "strike through").append(" normal" + NP).underline(
        "under line").append(" normal")
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def using_colors(msp, location):
    attribs = dict(ATTRIBS)
    attribs['width'] = 10.0
    editor = MTextEditor("using colors:" + NP)
    # Change colors by name: red, green, blue, yellow, cyan, magenta, white
    editor.color_name('red').append('RED' + NP)
    # The color stays the same until changed
    editor.append('also RED' + NP)
    # Change color by ACI (AutoCAD Color Index)
    editor.aci(3).append('GREEN' + NP)
    # Change color by RGB tuples
    editor.rgb((0, 0, 255)).append('BLUE' + NP)
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def changing_text_height_absolute(msp, location):
    attribs = dict(ATTRIBS)
    attribs['width'] = 40.0  # need mor space to avoid text wrapping
    editor = MTextEditor("changing text height absolute: default height is 0.7" + NP)
    # this is the default text height in the beginning:
    # The text height can only be changed by a factor:
    editor.height(1.4)  # scale by 2 = 1.4
    editor.append("text height: 1.4" + NP)
    editor.height(3.5).append("text height: 3.5" + NP)
    editor.height(0.7).append("back to default height: 0.7" + NP)
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def changing_text_height_relative(msp, location):
    attribs = dict(ATTRIBS)
    attribs['width'] = 40.0  # need mor space to avoid text wrapping
    editor = MTextEditor("changing text height relative: default height is 0.7" + NP)
    # this is the default text height in the beginning:
    current_height = attribs['char_height']
    # The text height can only be changed by a factor:
    editor.scale_height(2)  # scale by 2 = 1.4
    # keep track of the actual height:
    current_height *= 2
    editor.append("text height: 1.4" + NP)
    # to set an absolute height, calculate the required factor:
    desired_height = 3.5
    factor = desired_height / current_height
    editor.scale_height(factor).append("text height: 3.5" + NP)
    current_height = desired_height
    # and back to 0.7
    editor.scale_height(0.7 / current_height).append(
        "back to default height: 0.7" + NP)
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def create(dxfversion):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    recreate_mtext_py_example(msp, location=(0, 0))
    using_colors(msp, location=(0, 10))
    changing_text_height_absolute(msp, location=(0, 25))
    changing_text_height_relative(msp, location=(0, 40))
    doc.set_modelspace_vport(height=60, center=(15, 15))
    return doc


for dxfversion in ['R2000', 'R2004', 'R2007', 'R2010', 'R2013', 'R2018']:
    doc = create(dxfversion)
    filename = f"mtext_editor_{dxfversion}.dxf"
    doc.saveas(OUTBOX / filename)
    print(f"saved {filename}")
