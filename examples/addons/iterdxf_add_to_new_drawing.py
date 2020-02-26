# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
from pathlib import Path
from collections import Counter
import ezdxf
from ezdxf.addons import iterdxf

DIR = Path('~/Desktop/Outbox').expanduser()
BIGFILE = Path(r'D:\Source\dxftest\GKB-R2010.dxf')
# BIGFILE = Path(r'D:\Source\dxftest\ACAD_R2000.dxf')

doc = ezdxf.new()
msp = doc.modelspace()

print('Single Pass Modelspace Iterator:')
counter = Counter()
t0 = time.perf_counter()
for entity in iterdxf.single_pass_modelspace(open(BIGFILE, 'rb')):
    counter[entity.dxftype()] += 1
    try:
        msp.add_foreign_entity(entity)
    except ezdxf.DXFValueError:
        pass

ta = time.perf_counter() - t0
print(f'Processing time: {ta:.2f}s')

print('Saving as ezdxf.dxf')
doc.saveas(DIR / 'ezdxf.dxf')

