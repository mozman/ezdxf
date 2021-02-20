# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons import text2path
from ezdxf import zoom, disassemble
from ezdxf.lldxf import const

EXAMPLES = Path(__file__).parent.parent.parent / 'examples_dxf'
OUTBOX = Path('~/Desktop/Outbox').expanduser()
FILE1 = "text_mirror_true_type_font.dxf"
FILE2 = "text_oblique_rotate.dxf"

FILE = FILE2
doc = ezdxf.readfile(EXAMPLES / FILE)
doc.layers.new('OUTLINE', dxfattribs={'color': 1})
doc.layers.new('BBOX', dxfattribs={'color': 5})
msp = doc.modelspace()
text_entities = msp.query('TEXT')

# Convert TEXT entities into SPLINE and POLYLINE entities:
kind = text2path.Kind.SPLINES
for text in text_entities:
    for e in text2path.virtual_entities(text, kind=kind):
        e.dxf.layer = 'OUTLINE'
        e.dxf.color = const.BYLAYER
        msp.add_entity(e)

# Add bounding boxes
attrib = {'layer': 'BBOX'}
boxes = []

# The "primitive" representation for TEXT entities is the bounding box:
for prim in disassemble.to_primitives(text_entities):
    p = msp.add_lwpolyline(prim.vertices(), dxfattribs=attrib)
    boxes.append(p)

# Zoom on bounding boxes (fast):
zoom.objects(msp, boxes,factor=1.1)
doc.saveas(OUTBOX / FILE)
