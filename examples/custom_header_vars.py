# Copyright (c) 2014-2021, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

DIR = pathlib.Path("~/Desktop/Outbox").expanduser()


def custom_header_vars():
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_polyline2d(points)
    doc.header.custom_vars.append("Name", "Manfred Moitzi")
    doc.header.custom_vars.append("Adresse", "8020 Graz")
    doc.saveas(DIR / "custom_header_vars.dxf")


custom_header_vars()
