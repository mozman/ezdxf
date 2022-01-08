# Copyright (c) 2022 Manfred Moitzi
# License: MIT License
import argparse
import sys
import glob
import ezdxf
from ezdxf import recover
from ezdxf.addons import Importer


def fixed_by_ezdxf(filename):
    new_filename = filename.replace(".dxf", ".fix.dxf")
    # The original file is only readable but not to fix!
    doc, auditor = recover.readfile(filename)
    # Create a new valid DXF document:
    doc2 = ezdxf.new()
    # Import data into new document:
    importer = Importer(doc, doc2)
    importer.import_modelspace()
    importer.finalize()
    doc2.saveas(new_filename)
    print(f'saved fixed DXF file "{new_filename}"')


def recover_by_ezdxf(filename):
    # The original file is only readable but not to fix!
    new_filename = filename.replace(".dxf", ".rec.dxf")
    doc, auditor = recover.readfile(filename)
    doc.saveas(new_filename)
    print(f'saved recovered DXF file "{new_filename}"')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="+",
        help='DXF file to fix, wildcards "*" and "?" are supported',
    )
    args = parser.parse_args(sys.argv[1:])
    for pattern in args.file:
        for filename in glob.glob(pattern):
            # Injecting the subclass markers is no longer necessary due to the
            # use of the simple_dxfattribs_loader().
            recover_by_ezdxf(filename)
            fixed_by_ezdxf(filename)


# This fixes are specific to the DXF file provided for issue #604
if __name__ == "__main__":
    main()
