# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from pathlib import Path

import ezdxf
from ezdxf.addons import odafc

FILE = "colorwh.dwg"
OUTDIR = Path("~/Desktop/outbox").expanduser()

doc = odafc.readfile(ezdxf.options.test_files_path / "AutodeskSamples" / FILE)
if doc:
    msp = doc.modelspace()
    print(f"Filename: {doc.filename}")
    print(f"DXF Version: {doc.dxfversion} - {doc.acad_release}")
    print(f"Modelspace has {len(msp)} entities.")
    doc.saveas((OUTDIR / FILE).with_suffix(".dxf"))
