# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import time
import ezdxf
from collections import Counter
from ezdxf.addons import iterdxf

BIGFILE = ezdxf.options.test_files_path / "GKB-R2010.dxf"

# ------------------------------------------------------------------------------
# This example shows how iterate over very big DXF files without loading them
# into memory. This takes much longer, but it's maybe the only way to process
# these very large files.
#
# This example shows the difference of the tree supported iteration methods of
# the iterdxf add-on.
#
# docs: https://ezdxf.mozman.at/docs/addons/iterdxf.html#
# ------------------------------------------------------------------------------


def main():
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


if __name__ == "__main__":
    main()
