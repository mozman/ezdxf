# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import time
from ezdxf.lldxf.fileindex import load

CADKIT = Path("D:/Source/dxftest/CADKitSamples")

overall_time = 0.
overall_lines = 0
for name in CADKIT.glob('*.dxf'):
    t0 = time.perf_counter()
    file_structure = load(str(name))
    t = time.perf_counter() - t0
    count = sum(t.code == 0 for t in file_structure.index)
    lines = file_structure.index[-1].line
    overall_time += t
    overall_lines += lines
    print(f'File: "{Path(name).name}"\n  {lines} lines scanned\n  {count} structure tags\n  scan time: {t:.2f}s\n')

print(f'Overall time to scan: {overall_time:.2f}s')
print(f'Overall scanned lines: {overall_lines}')
