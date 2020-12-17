#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

from ezdxf import recover

doc, auditor = recover.readfile("cc_dxflib.dxf")

if auditor.has_fixes:
    auditor.print_fixed_errors()

if auditor.has_errors:
    auditor.print_error_report()
