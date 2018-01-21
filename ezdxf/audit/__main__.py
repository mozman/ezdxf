# Purpose: DXF Pretty Printer
# Created: 16.07.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import sys
import argparse
import os
import glob
from ezdxf import readfile, options
from ezdxf.lldxf.const import DXFError
from ezdxf.lldxf.validator import is_dxf_file


def audit(filename):
    try:
        dwg = readfile(filename, legacy_mode=True)
    except IOError:
        print("Unable to read DXF file '{}'.".format(filename))
        sys.exit(1)
    except DXFError as e:
        print(str(e))
        sys.exit(2)

    auditor = dwg.audit()
    auditor.print_report()


def print_msg(text):
    print(text)
    print('-'*len(text))


def main():
    print()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='+',
        help='audit DXF files',
    )
    args = parser.parse_args(sys.argv[1:])

    options.compress_binary_data = True
    for pattern in args.files:
        names = list(glob.glob(pattern))
        if len(names) == 0:
            print("File(s) '{}' not found.".format(pattern))
            continue
        for filename in names:
            if not os.path.exists(filename):
                print("File '{}' not found.".format(filename))
                continue
            if not is_dxf_file(filename):
                print("File '{}' is not a DXF file.".format(filename))
                continue
            print_msg('processing: {}'.format(filename))
            audit(filename)


if __name__ == "__main__":
    main()
