#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path

import ezdxf
from ezdxf.sections.headervars import HEADER_VAR_MAP

TEMPLATES = Path(ezdxf.EZDXF_TEST_FILES) / "templates"


def check_header_var_group_codes(doc):
    for name, value in doc.header.hdrvars.items():
        vardef = HEADER_VAR_MAP.get(name, None)
        if vardef is None:
            print(
                f"Unknown/new header variable: {name} in DXF version {doc.dxfversion}"
            )
        elif value.code != vardef.code:
            print(
                f"{name} DXF version {doc.dxfversion}: {value.code} != {vardef.code} "
            )
    # Current state of changed group codes (2021-04-03):
    # $XCLIPFRAME DXF version AC1018: 290 != 280
    # $XCLIPFRAME DXF version AC1021: 290 != 280
    # $ACADMAINTVER DXF version AC1032: 90 != 70


for filename in TEMPLATES.glob("*.dxf"):
    doc = ezdxf.readfile(str(filename))
    check_header_var_group_codes(doc)
