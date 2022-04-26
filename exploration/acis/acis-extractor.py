#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import cast
import sys
from pathlib import Path
from argparse import ArgumentParser
import ezdxf
from ezdxf.entities import Body

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

SEARCH_TYPES = {"3DSOLID", "REGION"}
DEFAULT_FILE = DIR / "acis.dxf"


def export_acis(entity: Body):
    version = entity.doc.dxfversion
    fname = f"{version}-{entity.dxftype()}-{entity.dxf.handle}"
    data = entity.acis_data
    if isinstance(data, bytes):
        with open(DIR / (fname + ".sab"), "wb") as fp:
            fp.write(data)
    else:
        with open(DIR / (fname + ".sat"), "wt") as fp:
            fp.write("\n".join(data))


def extract_acis(filepath: Path):
    print(f"processing file: {filepath}")
    try:
        doc = ezdxf.readfile(filepath)
    except IOError as e:
        print(str(e))
        sys.exit(1)
    msp = doc.modelspace()
    for e in msp:
        if e.dxftype() in SEARCH_TYPES:
            export_acis(cast("Body", e))


def main():
    parser = ArgumentParser()
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    if len(args.files):
        for filename in args.files:
            extract_acis(filename)
    else:
        extract_acis(DEFAULT_FILE)


if __name__ == "__main__":
    main()
