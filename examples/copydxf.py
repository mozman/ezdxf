# Copyright (c) 2011-2022, Manfred Moitzi
# License: MIT License
import sys
import time
import ezdxf
from ezdxf import recover

# ------------------------------------------------------------------------------
# copy DXF files by the recover module including an audit process
# ------------------------------------------------------------------------------


def copy_dxf(from_file: str, to_file: str):
    t0 = time.time()
    try:  # Fast path:
        doc, auditor = recover.readfile(from_file)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file: {from_file}.")
        sys.exit(2)

    t1 = time.time()
    print(f"loading and auditing time: {t1 - t0:.2f} seconds")

    if auditor.has_fixes:  # recovered errors
        auditor.print_fixed_errors()
    # The DXF file can still have unrecoverable errors, such files should
    # not be exported!
    if auditor.has_errors:
        print(f"Found unrecoverable errors in DXF file: {from_file}.")
        auditor.print_error_report()
        sys.exit(3)

    t0 = time.time()
    doc.saveas(to_file)
    t1 = time.time()
    print(f"export time: {t1 - t0:.2f} seconds")


if __name__ == "__main__":
    copy_dxf(sys.argv[1], sys.argv[2])
