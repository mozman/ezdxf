# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
from pathlib import Path
import ezdxf
from ezdxf.addons import iterdxf
BIGFILE = Path(ezdxf.EZDXF_TEST_FILES) / 'GKB-R2010.dxf'
# BIGFILE = Path(ezdxf.EZDXF_TEST_FILES) / 'ACAD_R2000.dxf'
OUTDIR = Path('~/Desktop/Outbox').expanduser()

t0 = time.perf_counter()
doc = iterdxf.opendxf(BIGFILE)
line_exporter = doc.export(OUTDIR / 'lines.dxf')
text_exporter = doc.export(OUTDIR / 'text.dxf')
polyline_exporter = doc.export(OUTDIR / 'polyline.dxf')
lwpolyline_exporter = doc.export(OUTDIR / 'lwpolyline.dxf')
try:
    for entity in doc.modelspace():
        if entity.dxftype() == 'LINE':
            line_exporter.write(entity)
        elif entity.dxftype() == 'TEXT':
            text_exporter.write(entity)
        elif entity.dxftype() == 'POLYLINE':
            polyline_exporter.write(entity)
        elif entity.dxftype() == 'LWPOLYLINE':
            lwpolyline_exporter.write(entity)
finally:
    line_exporter.close()
    text_exporter.close()
    polyline_exporter.close()
    lwpolyline_exporter.close()
    doc.close()

print(f'Processing time: {time.perf_counter()-t0:.2f}s')
