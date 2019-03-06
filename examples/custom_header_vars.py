# Created: 13.04.2014
# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
import ezdxf


def custom_header_vars():
    doc = ezdxf.new2('AC1015')
    msp = doc.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_polyline2d(points)
    doc.header.custom_vars.append("Name", "Manfred Moitzi")
    doc.header.custom_vars.append("Adresse", "8020 Graz")
    doc.saveas("custom_header_vars.dxf")


custom_header_vars()
