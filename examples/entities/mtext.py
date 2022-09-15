# Copyright (c) 2013-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example adds a MTEXT entity to the modelspace.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/mtext.html
# tutorial: https://ezdxf.mozman.at/docs/tutorials/mtext.html
# ------------------------------------------------------------------------------


doc = ezdxf.new("R2007", setup=True)
msp = doc.modelspace()
attribs = {
    "char_height": 0.7,
    "width": 5.0,
    "style": "OpenSans",
}
msp.add_line((-10, -1), (10, -2))
mtext = msp.add_mtext("This is a long MTEXT line with line wrapping!", attribs)
mtext.set_bg_color((108, 204, 193))

# line break \P
msp.add_mtext("Line 1\\PLine 2", attribs).set_location(insert=(0, 10))

attribs["width"] = 15
text = (
    "normal \\Oover strike\\o normal\\Pnormal \\Kstrike through\\k normal"
    "\\Pnormal \\Lunder line\\l normal"
)
msp.add_mtext(text, attribs).set_location(insert=(0, 15))
# see example "mtext_editor.py" how to use the MTextEditor to create the same
# result without complicated escape sequences.


filename = CWD / "mtext.dxf"
doc.saveas(filename)
print(f"saved {filename}")
