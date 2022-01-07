# Copyright (c) 2022 Manfred Moitzi
# License: MIT License
import argparse
import sys
import glob
import ezdxf
from ezdxf.lldxf.tagger import ascii_tags_loader
from ezdxf import recover
from ezdxf.addons import Importer


def inject_subclass_marker(filename):
    fixed_file = filename.replace(".dxf", ".fix.dxf")
    outfile = open(fixed_file, "wt", encoding="cp1252")
    infile = open(filename, "rt", encoding="cp1252")
    structure = ""
    for tag in ascii_tags_loader(infile):
        if tag.code == 0:
            structure = tag.value
        elif structure == "ELLIPSE":
            if tag.code == 10:
                outfile.write("100\nAcDbEllipse\n")
        elif structure == "TEXT":
            if tag.code == 8:
                outfile.write("100\nAcDbEntity\n")
            elif tag.code == 1:
                outfile.write("100\nAcDbText\n")
        outfile.write(tag.dxfstr())

    infile.close()
    outfile.close()
    return fixed_file


def recover_by_ezdxf(filename):
    # The original file is only readable but not to fix!
    doc, auditor = recover.readfile(filename)
    # Create a new valid DXF document:
    doc2 = ezdxf.new()
    # Import data into new document:
    importer = Importer(doc, doc2)
    importer.import_modelspace()
    importer.finalize()
    doc2.saveas(filename)


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
            new_filename = inject_subclass_marker(filename)
            recover_by_ezdxf(new_filename)


# This fixes are specific to the DXF file provided for issue #604
if __name__ == "__main__":
    main()
