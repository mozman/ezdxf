# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import random
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create a WIPEOUT entity.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/wipeout.html
# ------------------------------------------------------------------------------

MAX_SIZE = 100


def random_point():
    return random.random() * MAX_SIZE, random.random() * MAX_SIZE


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    for _ in range(30):
        msp.add_line(random_point(), random_point())

    msp.add_wipeout([(30, 30), (70, 70)])
    doc.set_modelspace_vport(center=(50, 50), height=MAX_SIZE)

    doc.saveas(CWD / "random_wipeout.dxf")


if __name__ == "__main__":
    main()
