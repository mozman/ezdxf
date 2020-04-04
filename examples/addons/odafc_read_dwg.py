# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
from ezdxf.addons import odafc

FILE = 'colorwh.dwg'
OUTDIR = Path('~/Desktop/outbox').expanduser()

doc = odafc.readfile(OUTDIR / FILE)
if doc:
    msp = doc.modelspace()
    print(f'Filename: {doc.filename}')
    print(f'DXF Version: {doc.dxfversion} - {doc.acad_release}')
    print(f'Modelspace has {len(msp)} entities.')
    doc.save()
