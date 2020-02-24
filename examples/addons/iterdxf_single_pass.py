# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
from pathlib import Path
from ezdxf.addons import iterdxf
BIGFILE = Path(r'D:\Source\dxftest\GKB-R2010.dxf')
# BIGFILE = Path(r'D:\Source\dxftest\ACAD_R2000.dxf')

t0 = time.perf_counter()
lines = 0
text = 0
polylines = 0
lwpolylines = 0
for entity in iterdxf.single_pass_modelspace(BIGFILE):
    if entity.dxftype() == 'LINE':
        lines += 1
    elif entity.dxftype() == 'TEXT':
        text += 1
    elif entity.dxftype() == 'POLYLINE':
        polylines += 1
    elif entity.dxftype() == 'LWPOLYLINE':
        lwpolylines += 1

print(f'Processing time: {time.perf_counter()-t0:.2f}s')
print(f'Lines: {lines}')
print(f'Text: {text}')
print(f'Polylines: {polylines}')
print(f'LWPolylines: {lwpolylines}')
