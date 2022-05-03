#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import sys
from pathlib import Path
from argparse import ArgumentParser
import ezdxf
from ezdxf.entities import Body

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

DEFAULT_FILE = DIR / "acis.dxf"


def export_acis(entity: Body, folder: Path):
    version = entity.doc.dxfversion
    fname = f"{version}-{entity.dxftype()}-{entity.dxf.handle}"
    data = entity.acis_data
    if isinstance(data[0], bytes):
        with open(folder / (fname + ".sab"), "wb") as fp:
            print(f"Exporting: {fp.name}")
            fp.write(b"".join(data))
    else:
        with open(folder / (fname + ".sat"), "wt") as fp:
            print(f"Exporting: {fp.name}")
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
        if isinstance(e, Body):
            export_acis(e, folder=filepath.parent)


def main():
    parser = ArgumentParser()
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    if len(args.files):
        for filename in args.files:
            extract_acis(Path(filename))
    else:
        extract_acis(DEFAULT_FILE)


if __name__ == "__main__":
    main()
