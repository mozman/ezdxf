# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
import pathlib
from collections import Counter
import ezdxf
from ezdxf.addons import iterdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how iterate over very big DXF files without loading them
# into memory. This takes much longer, but it's maybe the only way to process
# these very large files.
#
# This example uses the modelspace iterator to copy all supported entities from
# modelspace without any resources defined in the source DXF document.
# ------------------------------------------------------------------------------

BIGFILE = ezdxf.options.test_files_path / "GKB-R2010.dxf"


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    print("Modelspace Iterator:")
    counter = Counter()
    t0 = time.perf_counter()
    for entity in iterdxf.modelspace(BIGFILE):
        counter[entity.dxftype()] += 1
        try:
            msp.add_foreign_entity(entity)
        except ezdxf.DXFTypeError:
            pass

    ta = time.perf_counter() - t0
    print(f"Processing time: {ta:.2f}s")

    print("Saving as ezdxf.dxf")
    doc.saveas(CWD / "ezdxf.dxf")


if __name__ == '__main__':
    main()
