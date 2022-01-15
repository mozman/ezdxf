#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
# This is the example provided by the py3dbp package:
from pathlib import Path
from ezdxf.math import Vec3
from ezdxf.addons import binpacking

DIR = Path("~/Desktop/Outbox").expanduser()


def build_packer():
    packer = binpacking.Packer()
    packer.add_box("small-envelope", 12, 6, 1, 2000)
    packer.add_box("large-envelope", 15, 12, 1, 2000)
    packer.add_box("small-box", 8, 6, 1, 2000)
    packer.add_box("medium-box", 11, 9, 5, 2000)
    packer.add_box("medium-2-box", 14, 12, 4, 2000)
    packer.add_box("large-box", 12, 12, 5, 2000)
    packer.add_box("large-2-box", 24, 12, 3, 2000)

    packer.add_item("50g [powder 1]", 4, 2, 2, 50)
    packer.add_item("50g [powder 2]", 4, 2, 2, 50)
    packer.add_item("50g [powder 3]", 4, 2, 2, 50)
    packer.add_item("250g [powder 4]", 8, 4, 2, 250)
    packer.add_item("250g [powder 5]", 8, 4, 2, 250)
    packer.add_item("250g [powder 6]", 8, 4, 2, 250)
    packer.add_item("250g [powder 7]", 8, 4, 2, 250)
    packer.add_item("250g [powder 8]", 8, 4, 2, 250)
    packer.add_item("250g [powder 9]", 8, 4, 2, 250)
    return packer


def main(filename):
    packer = build_packer()
    packer.pack(pick_strategy=binpacking.PickStrategy.SMALLER_FIRST)
    doc = binpacking.export_dxf(packer, Vec3(0, 0, 1))
    doc.saveas(filename)


if __name__ == '__main__':
    main(DIR / "example.dxf")