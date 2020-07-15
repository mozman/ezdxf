# Purpose: audit runner
# Created: 21.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
import sys
import argparse
import os
import glob
from ezdxf import readfile, options
from ezdxf.lldxf.const import DXFError
from ezdxf.lldxf.validator import is_dxf_file


def audit(filename: str, ignore_zero_pointers: bool = False) -> None:
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
    auditor.print_error_report(errors)


def processing_msg(text: str) -> None:
    print(text)
    print('-' * len(text))


def main() -> None:
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
            processing_msg(filename)
            audit(filename)


if __name__ == "__main__":
    main()
