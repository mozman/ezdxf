# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import ezdxf
import os
from collections import Counter
import time
from ezdxf import EZDXF_TEST_FILES, bbox

CADKIT = "CADKitSamples"
CADKIT_FILES = [
    "A_000217.dxf",  # 0
    "AEC Plan Elev Sample.dxf",  # 1
    "backhoe.dxf",  # 2
    "BIKE.DXF",  # 3
    "cnc machine.dxf",  # 4
    "Controller-M128-top.dxf",  # 5
    "drilling_machine.dxf",  # 6
    "fanuc-430-arm.dxf",  # 7
    "Floor plan.dxf",  # 8
    "gekko.DXF",  # 9
    "house design for two family with comman staircasedwg.dxf",  # 10
    "house design.dxf",  # 11
    "kit-dev-coldfire-xilinx_5213.dxf",  # 12
    "Laurana50k.dxf",  # 13
    "Lock-Off.dxf",  # 14
    "Mc Cormik-D3262.DXF",  # 15
    "Mechanical Sample.dxf",  # 16
    "Nikon_D90_Camera.DXF",  # 17
    "pic_programmer.dxf",  # 18
    "Proposed Townhouse.dxf",  # 19
    "Shapefont.dxf",  # 20
    "SMA-Controller.dxf",  # 21
    "Tamiya TT-01.DXF",  # 22
    "torso_uniform.dxf",  # 23
    "Tyrannosaurus.DXF",  # 24
    "WOOD DETAILS.dxf",  # 25
]

STD_FILES = [
    CADKIT_FILES[1],
    CADKIT_FILES[23],
]


def count_entities(msp):
    counter = Counter()
    for entity in msp:
        counter[entity.dxftype()] += 1
    return counter


def print_bbox(box):
    print(
        f"  EXTMIN = {box.extmin.x:.3f}, {box.extmin.y:.3f}, {box.extmin.z:.3f}"
    )
    print(
        f"  EXTMAX = {box.extmax.x:.3f}, {box.extmax.y:.3f}, {box.extmax.z:.3f}"
    )


worse = 0
count = 0
sum_precise = 0.0
sum_fast = 0.0
USE_MATPLOTLIB = False
PRELOAD_CACHE = False
print(f"preloading matplotlib cache: {PRELOAD_CACHE}")
print(f"using matplotlib for fast bounding box calculation: {USE_MATPLOTLIB}")

for _name in CADKIT_FILES:
    ezdxf.options.use_matplotlib = True
    count += 1
    filename = os.path.join(EZDXF_TEST_FILES, CADKIT, _name)
    print(f"reading file: {filename}")
    t0 = time.perf_counter()
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    print(f"loading time: {time.perf_counter() - t0:.3f} sec")
    if PRELOAD_CACHE:
        print("preloading matplotlib font caches ...")
        bbox.extents(doc.modelspace(), flatten=0)

    t0 = time.perf_counter()
    box0 = bbox.extents(doc.modelspace(), flatten=0.01)
    precise_result = time.perf_counter() - t0
    sum_precise += precise_result
    print(f"precise bounding box calculation in {precise_result:.3f} sec")

    ezdxf.options.use_matplotlib = USE_MATPLOTLIB
    t0 = time.perf_counter()
    box1 = bbox.extents(doc.modelspace(), flatten=0)
    fast_result = time.perf_counter() - t0
    sum_fast += fast_result
    print(f"fast bounding box calculation in {fast_result:.3f} sec")

    extents = box0.size
    diff = extents - box1.size
    print(f"bounding box difference:")
    print(f"    in drawing units: x= {diff.x:.3f}, y= {diff.y:.3f}")
    print(
        f"    in percent: x= {diff.x/extents.x*100:.1f}%, y= {diff.y/extents.y*100:.1f}%"
    )

    ratio = precise_result / fast_result
    print(f"ratio precise/fast: {ratio:.3f}")
    if ratio < 1.0:
        worse += 1
        print("+" * 79)
        print("PRECISE calculation was faster!")

    print("-" * 79)

print(
    f"{worse} of {count} PRECISE bounding box calculations were faster than the FAST method."
)
ratio = sum_precise / sum_fast if sum_fast > 0 else 9999
print(
    f"overall runtime precise/fast: {sum_precise:.1f}/{sum_fast:.1f}, ratio: {ratio:.1f}"
)
