# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import odafc

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to read DWG files by the "Open Design Alliance File Converter" (odafc).
#
# docs: https://ezdxf.mozman.at/docs/addons/odafc.html
# ------------------------------------------------------------------------------

FILE = "colorwh.dwg"

doc = odafc.readfile(ezdxf.options.test_files_path / "AutodeskSamples" / FILE)
if doc:
    msp = doc.modelspace()
    print(f"Filename: {doc.filename}")
    print(f"DXF Version: {doc.dxfversion} - {doc.acad_release}")
    print(f"Modelspace has {len(msp)} entities.")
    doc.saveas((CWD / FILE).with_suffix(".dxf"))
