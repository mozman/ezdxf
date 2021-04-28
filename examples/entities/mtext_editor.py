# Copyright (c) 2021 Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.tools.text import (
    MTextEditor, ParagraphProperties, MTextParagraphAlignment,
)
from ezdxf.tools.text_layout import lorem_ipsum

OUTBOX = Path("~/Desktop/Outbox").expanduser()
ATTRIBS = {
    "char_height": 0.7,
    "style": "OpenSans",
}

# use constants defined in MTextEditor:
NP = MTextEditor.NEW_PARAGRAPH


def recreate_mtext_py_example(msp, location):
    # replicate example "mtext.py":
    attribs = dict(ATTRIBS)
    attribs["width"] = 15.0
    editor = MTextEditor(f"recreate mtext.py result:{NP}normal ").overline(
        "over line").append(" normal" + NP + "normal ").strike_through(
        "strike through").append(" normal" + NP).underline(
        "under line").append(" normal")
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def using_colors(msp, location):
    attribs = dict(ATTRIBS)
    attribs["width"] = 10.0
    editor = MTextEditor("using colors:" + NP)
    # Change colors by name: red, green, blue, yellow, cyan, magenta, white
    editor.color("red").append("RED" + NP)
    # The color stays the same until changed
    editor.append("also RED" + NP)
    # Change color by ACI (AutoCAD Color Index)
    editor.aci(3).append("GREEN" + NP)
    # Change color by RGB tuples
    editor.rgb((0, 0, 255)).append("BLUE" + NP)
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def changing_text_height_absolute(msp, location):
    attribs = dict(ATTRIBS)
    attribs["width"] = 40.0  # need mor space to avoid text wrapping
    editor = MTextEditor(
        "changing text height absolute: default height is 0.7" + NP)
    # this is the default text height in the beginning:
    # The text height can only be changed by a factor:
    editor.height(1.4)  # scale by 2 = 1.4
    editor.append("text height: 1.4" + NP)
    editor.height(3.5).append("text height: 3.5" + NP)
    editor.height(0.7).append("back to default height: 0.7" + NP)
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def changing_text_height_relative(msp, location):
    attribs = dict(ATTRIBS)
    attribs["width"] = 40.0  # need mor space to avoid text wrapping
    editor = MTextEditor(
        "changing text height relative: default height is 0.7" + NP)
    # this is the default text height in the beginning:
    current_height = attribs["char_height"]
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


def changing_fonts(msp, location):
    attribs = dict(ATTRIBS)
    attribs["width"] = 15.0
    editor = MTextEditor("changing fonts:" + NP)
    editor.append("Default: Hello World!" + NP)
    editor.append("SimSun: ")
    # The font name for changing MTEXT fonts inline is the font family name!
    # The font family name is the name shown in font selection widgets in
    # desktop applications: "Arial", "Times New Roman", "Comic Sans MS"
    #
    # change font in a group to revert back to the default font at the end:
    simsun_editor = MTextEditor().font("SimSun").append("你好，世界" + NP)
    # reverts the font back at the end of the group:
    editor.group(str(simsun_editor))
    # back to default font OpenSans:
    editor.append("Times New Roman: ")
    # change font outside of a group until next font change:
    editor.font("Times New Roman").append("Привет мир!" + NP)
    # If the font does not exist, a replacement font will be used:
    editor.font("Does not exist").append("This is the replacement font!")
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def indent_first_line(msp, location):
    attribs = dict(ATTRIBS)
    attribs["char_height"] = 0.25
    attribs["width"] = 7.5
    editor = MTextEditor("Indent the first line:" + NP)
    props = ParagraphProperties(
        indent=1,  # indent first line
        align=MTextParagraphAlignment.JUSTIFIED
    )
    editor.paragraph(props)
    editor.append(" ".join(lorem_ipsum(100)))
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def indent_except_fist_line(msp, location):
    attribs = dict(ATTRIBS)
    attribs["char_height"] = 0.25
    attribs["width"] = 7.5
    editor = MTextEditor("Indent left paragraph side:" + NP)
    indent = 0.7
    props = ParagraphProperties(
        # first line indentation is relative to "left", this reverses the
        # left indentation:
        indent=-indent,  # first line
        # indent left paragraph side:
        left=indent,
        align=MTextParagraphAlignment.JUSTIFIED
    )
    editor.paragraph(props)
    editor.append(" ".join(lorem_ipsum(100)))
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def bullet_list(msp, location):
    attribs = dict(ATTRIBS)
    attribs["char_height"] = 0.25
    attribs["width"] = 7.5
    # There are no special commands to build bullet list, the list is build of
    # indentation and a tabulator stop. Each list item needs a marker as an
    # arbitrary string.
    bullet = "•"  # alt + numpad 7
    editor = MTextEditor("Bullet List:" + NP)
    editor.bullet_list(
        indent=1,
        bullets=[bullet] * 3,  # each list item needs a marker
        content=[
            "First item",
            "Second item",
            " ".join(lorem_ipsum(30)),
        ])
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def numbered_list(msp, location):
    attribs = dict(ATTRIBS)
    attribs["char_height"] = 0.25
    attribs["width"] = 7.5
    # There are no special commands to build numbered list, the list is build of
    # indentation and a tabulator stop. There is no automatic numbering,
    # but therefore the absolute freedom for using any string as list marker:
    editor = MTextEditor("Numbered List:" + NP)
    editor.bullet_list(
        indent=1,
        bullets=["1.", "2.", "3."],
        content=[
            "First item",
            "Second item",
            " ".join(lorem_ipsum(30)),
        ])
    msp.add_mtext(str(editor), attribs).set_location(insert=location)


def create(dxfversion):
    """
    Important:

        MTEXT FORMATTING IS NOT PORTABLE ACROSS CAD APPLICATIONS!

    Inline MTEXT codes are not supported by every CAD application and even
    if inline codes are supported the final rendering may vary.
    Inline codes are very well supported by AutoCAD (of course!) and BricsCAD,
    but don't expect the same rendering in other CAD applications.

    The drawing add-on of ezdxf may support some features in the future,
    but very likely with a different rendering result than AutoCAD/BricsCAD.

    """
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    recreate_mtext_py_example(msp, location=(0, 0))
    using_colors(msp, location=(0, 10))
    changing_text_height_absolute(msp, location=(0, 25))
    changing_text_height_relative(msp, location=(0, 40))
    changing_fonts(msp, location=(15, 14))
    indent_first_line(msp, location=(15, 6))
    indent_except_fist_line(msp, location=(24, 6))
    bullet_list(msp, location=(33, 6))
    numbered_list(msp, location=(33, 2))
    doc.set_modelspace_vport(height=60, center=(15, 15))
    return doc


for dxfversion in ["R2000", "R2004", "R2007", "R2010", "R2013", "R2018"]:
    doc = create(dxfversion)
    filename = f"mtext_editor_{dxfversion}.dxf"
    doc.saveas(OUTBOX / filename)
    print(f"saved {filename}")
