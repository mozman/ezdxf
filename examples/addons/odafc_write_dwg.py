# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path

import ezdxf
from ezdxf.addons import odafc

OUTDIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new(setup=True)
msp = doc.modelspace()

msp.add_text('DXF File created by ezdxf.')

odafc.export_dwg(doc, OUTDIR / 'xyz.dwg')
