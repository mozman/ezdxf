# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
from pathlib import Path
from collections import Counter
from ezdxf import EZDXF_TEST_FILES
from ezdxf.addons import iterdxf

BIGFILE = Path(EZDXF_TEST_FILES) / "GKB-R2010.dxf"
# BIGFILE = Path(EZDXF_TEST_FILES) / 'ACAD_R2000.dxf'

name = "iterdxf.opendxf()"
print(f"{name}\n{len(name) * '-'}")
counter = Counter()
t0 = time.perf_counter()
doc = iterdxf.opendxf(BIGFILE)
for entity in doc.modelspace():
    counter[entity.dxftype()] += 1
doc.close()

tb = time.perf_counter() - t0
print(f"Processing time: {tb:.2f}s")
print(counter)
print()

name = "iterdxf.single_pass_modelspace()"
print(f"{name}\n{len(name) * '-'}")
counter = Counter()
t0 = time.perf_counter()
for entity in iterdxf.single_pass_modelspace(
    open(BIGFILE, "rb"), types=["LINE"]
):
    counter[entity.dxftype()] += 1

ta = time.perf_counter() - t0
print(f"Processing time: {ta:.2f}s")
print(counter)
print(f"Advantage {name}: {((tb / ta) - 1) * 100.:.0f}%\n")

name = "iterdxf.modelspace()"
print(f"{name}\n{len(name) * '-'}")
counter = Counter()
t0 = time.perf_counter()
for entity in iterdxf.modelspace(BIGFILE, types=["LINE"]):
    counter[entity.dxftype()] += 1

tc = time.perf_counter() - t0
print(f"Processing time: {tc:.2f}s")
print(counter)
print(f"Advantage {name}: {((tb / tc) - 1) * 100.:.0f}%\n")
