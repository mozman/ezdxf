# Purpose: audit runner
# Created: 21.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

import sys
import argparse
import os
import glob
from ezdxf import readfile, options
from ezdxf.lldxf.const import DXFError
from ezdxf.lldxf.validator import is_dxf_file


def audit(filename, ignore_zero_pointers=False):
    try:
        dwg = readfile(filename, legacy_mode=True)
    except IOError:
        print("Unable to read DXF file '{}'.".format(filename))
        sys.exit(1)
    except DXFError as e:
        print(str(e))
        sys.exit(2)

    auditor = dwg.auditor()
    errors = auditor.run()
    if ignore_zero_pointers:
        errors = auditor.filter_zero_pointers(errors)
    auditor.print_report(errors)


def processing_msg(text):
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
    parser.add_argument(
        '-z', '--ignore_zero_pointers',
        action='store_true',
        help='ignore zero pointers',
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
            processing_msg(filename)
            audit(filename, args.ignore_zero_pointers)


if __name__ == "__main__":
    main()
