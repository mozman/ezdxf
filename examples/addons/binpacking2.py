#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
# This is the example provided by the py3dbp package:
from pathlib import Path
from ezdxf.math import Vec3
from ezdxf.addons import binpacking

DIR = Path("~/Desktop/Outbox").expanduser()


def build_packer():
    packer = binpacking.Packer()
    packer.add_bin("small-envelope", 11.5, 6.125, 0.25, 10)
    packer.add_bin("large-envelope", 15.0, 12.0, 0.75, 15)
    packer.add_bin("small-box", 8.625, 5.375, 1.625, 70.0)
    packer.add_bin("medium-box", 11.0, 8.5, 5.5, 70.0)
    packer.add_bin("medium-2-box", 13.625, 11.875, 3.375, 70.0)
    packer.add_bin("large-box", 12.0, 12.0, 5.5, 70.0)
    packer.add_bin("large-2-box", 23.6875, 11.75, 3.0, 70.0)

    packer.add_item("50g [powder 1]", 3.9370, 1.9685, 1.9685, 1)
    packer.add_item("50g [powder 2]", 3.9370, 1.9685, 1.9685, 2)
    packer.add_item("50g [powder 3]", 3.9370, 1.9685, 1.9685, 3)
    packer.add_item("250g [powder 4]", 7.8740, 3.9370, 1.9685, 4)
    packer.add_item("250g [powder 5]", 7.8740, 3.9370, 1.9685, 5)
    packer.add_item("250g [powder 6]", 7.8740, 3.9370, 1.9685, 6)
    packer.add_item("250g [powder 7]", 7.8740, 3.9370, 1.9685, 7)
    packer.add_item("250g [powder 8]", 7.8740, 3.9370, 1.9685, 8)
    packer.add_item("250g [powder 9]", 7.8740, 3.9370, 1.9685, 9)
    return packer


def main(filename):
    packer = build_packer()
    packer.pack(pick_strategy=binpacking.PickStrategy.BIGGER_FIRST)
    doc = binpacking.export_dxf(packer, offset=(0, 20, 0))
    doc.saveas(filename)


if __name__ == '__main__':
    main(DIR / "example.dxf")