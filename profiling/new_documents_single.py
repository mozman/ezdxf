#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import time
import ezdxf
N = 10000
t0 = time.perf_counter()
for _ in range(N):
    ezdxf.new()
t = time.perf_counter()-t0
print(f"created {int(N / t)} DXF drawings per second")
