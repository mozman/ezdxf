# Copyright (c) 2021, Manfred Moitzi
# License: MIT License

import pathlib
import ezdxf
from ezdxf import disassemble, zoom
from ezdxf.tools import fonts

DIR = pathlib.Path('~/Desktop/Outbox').expanduser()
fonts.load()

FILES = [
    'text_fonts.dxf',
    'text_oblique_rotate.dxf',
    'text_mirror_true_type_font.dxf',
    'text_stacked_shx_font.dxf',
]
for filename in FILES:
    print(f"Processing: {filename}")
    doc = ezdxf.readfile(
        pathlib.Path(__file__).parent.parent / 'examples_dxf' / filename)
    msp = doc.modelspace()

    # required to switch layer on/off
    doc.layers.new('TEXT_FRAME', dxfattribs={'color': 6})
    for frame in disassemble.to_primitives(msp.query('TEXT')):
        msp.add_lwpolyline(frame.vertices(), close=True,
                           dxfattribs={'layer': 'TEXT_FRAME'})

    zoom.extents(msp, factor=1.1)
    doc.saveas(DIR / filename)
