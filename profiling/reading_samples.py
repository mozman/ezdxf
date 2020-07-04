# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import ezdxf
import os
from collections import Counter
import time
from pympler import tracker

CADKIT = r"D:\Source\dxftest\CADKitSamples"
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
    r"D:\Source\dxftest\ACAD_R12.dxf",
    r"D:\Source\dxftest\FW25-R12.dxf",
]


def count_entities(msp):
    counter = Counter()
    for entity in msp:
        counter[entity.dxftype()] += 1
    return counter


PYMPLER = False

for _name in STD_FILES:
    filename = os.path.join(CADKIT, _name)
    print(f'reading file: {filename}')
    if PYMPLER:
        tr_new = tracker.SummaryTracker()
    start_reading = time.perf_counter()
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    new_entities = count_entities(msp)
    new_count = len(msp)
    new_timing = time.perf_counter() - start_reading
    if PYMPLER:
        tr_new.print_diff()
    print(f'loaded {new_count} entities in {new_timing:.1f} sec')
