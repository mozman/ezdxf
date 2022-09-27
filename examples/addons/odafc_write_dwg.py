# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import odafc

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to export DWG files by the "Open Design Alliance File Converter" (odafc).
#
# docs: https://ezdxf.mozman.at/docs/addons/odafc.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    msp.add_text("DXF File created by ezdxf.")
    odafc.export_dwg(doc, str(CWD / "xyz.dwg"))


if __name__ == "__main__":
    main()
