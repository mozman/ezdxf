# Purpose: using splines
# Created: 13.04.2014
# Copyright (c) , Manfred Moitzi
# License: MIT License
import ezdxf


def custom_header_vars():
    dwg = ezdxf.new('AC1015')
    msp = dwg.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_polyline2d(points)
    dwg.header.custom_vars.append("Name", "Manfred Moitzi")
    dwg.header.custom_vars.append("Adresse", "8020 Graz")
    dwg.saveas("custom_header_vars.dxf")


custom_header_vars()
