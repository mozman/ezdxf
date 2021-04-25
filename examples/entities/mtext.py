# Copyright (c) 2013-2021 Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf

OUTBOX = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new('R2007', setup=True)
msp = doc.modelspace()
attribs = {
    'char_height': 0.7,
    'width': 5.0,
    'style': 'OpenSans',
}
msp.add_line((-10, -1), (10, -2))
mtext = msp.add_mtext("This is a long MTEXT line with line wrapping!", attribs)
mtext.set_bg_color((108, 204, 193))

# line break \P
msp.add_mtext("Line 1\\PLine 2", attribs).set_location(insert=(0, 10))

attribs['width'] = 15
text = "normal \\Oover strike\\o normal\\Pnormal \\Kstrike trough\\k normal" \
       "\\Pnormal \\Lunder line\\l normal"
msp.add_mtext(text, attribs).set_location(insert=(0, 15))
# see example "mtext_editor.py" how to use the MTextEditor to create the same
# result without complicated escape sequences.


filename = 'mtext.dxf'
doc.saveas(OUTBOX / filename)
print(f"saved {filename}")
