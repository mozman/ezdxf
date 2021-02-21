#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import os
import glob
from ezdxf.lldxf import const


def audit(args):
    """ Launcher sub-command: audit """
    from ezdxf import recover
    from ezdxf.lldxf.validator import is_dxf_file

    def processing_msg(text: str) -> None:
        print(text)
        print('-' * len(text))

    def _audit(filename: str) -> None:
        try:
            doc, auditor = recover.readfile(filename)
        except IOError:
            print(f'Not a DXF file or a generic I/O error.')
            sys.exit(1)
        except const.DXFStructureError:
            print(f'Invalid or corrupted DXF file.')
            sys.exit(2)

        if auditor.has_errors:
            auditor.print_error_report()
        if auditor.has_fixes:
            auditor.print_fixed_errors()
        if auditor.has_errors is False and auditor.has_fixes is False:
            print('No errors found.')

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
            _audit(filename)


def draw(args):
    print("draw")


def view(args):
    print("view")
