# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
from pathlib import Path
from collections import Counter
from ezdxf.addons import iterdxf
BIGFILE = Path(r'D:\Source\dxftest\GKB-R2010.dxf')
# BIGFILE = Path(r'D:\Source\dxftest\ACAD_R2000.dxf')


print('Single Pass Modelspace Iterator:')
counter = Counter()
t0 = time.perf_counter()
for entity in iterdxf.single_pass_modelspace(open(BIGFILE, 'rb')):
    counter[entity.dxftype()] += 1

ta = time.perf_counter()-t0
print(f'Processing time: {ta:.2f}s')
print(counter)

print('iterdxf.opendxf() Iterator:')
counter = Counter()
t0 = time.perf_counter()
doc = iterdxf.opendxf(BIGFILE)
for entity in doc.modelspace():
    counter[entity.dxftype()] += 1
doc.close()

tb = time.perf_counter()-t0
print(f'Processing time: {tb:.2f}s')
print(counter)

print(f'\nAdvantage Single Pass Iterator: {((tb/ta)-1)*100.:.0f}%')
