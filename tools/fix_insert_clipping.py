# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
#
# Fixes clipping issues of INSERT entities created by ezdxf older than v1.4.2b0
#
import ezdxf
from ezdxf.entities import Insert

DXF_FILE = "your.dxf"
RECOVER_FILE = "recover.dxf"


def fix_clipping(insert: Insert) -> None:
    if not insert.has_extension_dict:
        return
    xdict = insert.get_extension_dict()
    acad_filter = xdict.get("ACAD_FILTER")
    if acad_filter:
        acad_filter.dxf.hard_owned = 1
        print(f"Updated clipping path of {insert}.")


def main(filename: str, recover_file: str):
    doc = ezdxf.readfile(filename)
    for insert in doc.entitydb.query("INSERT"):
        fix_clipping(insert)
    doc.saveas(recover_file)


if __name__ == "__main__":
    main(DXF_FILE, RECOVER_FILE)
