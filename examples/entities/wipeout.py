# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import random
import ezdxf

DIR = Path("~/Desktop/Outbox").expanduser()
MAX_SIZE = 100

doc = ezdxf.new()
msp = doc.modelspace()


def random_point():
    return random.random() * MAX_SIZE, random.random() * MAX_SIZE


for _ in range(30):
    msp.add_line(random_point(), random_point())

msp.add_wipeout([(30, 30), (70, 70)])
doc.set_modelspace_vport(center=(50, 50), height=MAX_SIZE)

doc.saveas(DIR / "random_wipeout.dxf")
