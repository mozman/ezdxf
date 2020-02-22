# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
from ezdxf.addons import iterdxf
BIGFILE = Path(r'D:\Source\dxftest\GKB-R2010.dxf')
OUTDIR = Path('~/Desktop/Outbox').expanduser()

doc = iterdxf.opendxf(BIGFILE)
line_exporter = doc.export(OUTDIR / 'lines.dxf')
text_exporter = doc.export(OUTDIR / 'text.dxf')
polyline_exporter = doc.export(OUTDIR / 'polyline.dxf')
try:
    for entity in doc.modelspace():
        if entity.dxftype() == 'LINE':
            line_exporter.write(entity)
        elif entity.dxftype() == 'TEXT':
            text_exporter.write(entity)
        elif entity.dxftype() == 'POLYLINE':
            polyline_exporter.write(entity)
finally:
    line_exporter.close()
    text_exporter.close()
    polyline_exporter.close()
    doc.close()
