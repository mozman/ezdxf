#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

for version in ["R12", "R2000", "R2004", "R2007", "R2010", "R2013", "R2018"]:
    doc = ezdxf.new(dxfversion=version, setup=True)
    msp = doc.modelspace()

    msp.add_line((0, 0), (10, 10))
    doc.saveas(CWD / f"setup_{version}.dxf")
