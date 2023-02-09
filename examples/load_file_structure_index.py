# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import time
import ezdxf
from ezdxf.lldxf.fileindex import load

CADKIT = pathlib.Path(ezdxf.EZDXF_TEST_FILES) / "CADKitSamples"

# ------------------------------------------------------------------------------
# create FileStructure instances from CADKitSamples
#
# This example shows how fast Python can load DXF files without interpretation,
# this marks the lower bound for loading optimizations.
# ------------------------------------------------------------------------------


def main():
    overall_time = 0.0
    overall_lines = 0
    for name in CADKIT.glob("*.dxf"):
        t0 = time.perf_counter()
        file_structure = load(str(name))
        t = time.perf_counter() - t0
        count = sum(t.code == 0 for t in file_structure.index)
        lines = file_structure.index[-1].line
        overall_time += t
        overall_lines += lines
        print(
            f'File: "{pathlib.Path(name).name}"\n  {lines} '
            f"lines scanned\n  {count} "
            f"structure tags\n  scan time: {t:.2f}s\n"
        )

    print(f"Overall time to scan: {overall_time:.2f}s")
    print(f"Overall scanned lines: {overall_lines}")


if __name__ == "__main__":
    main()
