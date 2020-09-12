# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
import sys
import argparse
import os
import glob
import ezdxf
from ezdxf import recover
from ezdxf.lldxf.validator import is_dxf_file


def audit(filename: str, safe=False) -> None:
    try:
        if safe:
            print('Running in recover mode.')
            doc, auditor = recover.readfile(filename)
        else:
            doc = ezdxf.readfile(filename)
            auditor = doc.audit()
    except IOError:
        print(f"Unable to read DXF file '{filename}'.")
        sys.exit(1)
    except ezdxf.DXFStructureError as e:
        print(str(e))
        sys.exit(2)

    if auditor.has_errors:
        auditor.print_error_report()
    if auditor.has_fixes:
        auditor.print_fixed_errors()


def processing_msg(text: str) -> None:
    print(text)
    print('-' * len(text))


def main() -> None:
    print()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', '--recover',
        dest='recover',
        action='store_true',
        help='use recover mode to load files with DXF structure errors'
    )
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='+',
        help='audit DXF files',
    )

    args = parser.parse_args(sys.argv[1:])

    ezdxf.options.compress_binary_data = True
    for pattern in args.files:
        names = list(glob.glob(pattern))
        if len(names) == 0:
            print(f"File(s) '{pattern}' not found.")
            continue
        for filename in names:
            if not os.path.exists(filename):
                print(f"File '{filename}' not found.")
                continue
            if not is_dxf_file(filename):
                print(f"File '{filename}' is not a DXF file.")
                continue
            processing_msg(filename)
            audit(filename, safe=args.recover)


if __name__ == "__main__":
    main()
