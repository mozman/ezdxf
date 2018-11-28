# Purpose: using true color and transparency
# Created: 04.07.2015
# Copyright (c) 2015 Manfred Moitzi
# License: MIT License
import ezdxf


def lwpolyline_with_true_color():
    dwg = ezdxf.new('AC1018')  # for true color and transparency is DXF version AC1018 (ACAD R2004) or newer necessary
    msp = dwg.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_lwpolyline(points, dxfattribs={
        'color': 2,
        'true_color': ezdxf.rgb2int((38, 140, 89))  # true color has higher priority than the color attribute
    })
    dwg.saveas("true_color_lwpolyline.dxf")


# Another way to set true color values for DXF entities: Property DXFEntity.rgb
def lines_with_true_color():
    dwg = ezdxf.new('AC1018')  # for true color and transparency is DXF version AC1018 (ACAD R2004) or newer necessary
    msp = dwg.modelspace()
    for y in range(10):
        line = msp.add_line((0, y * 10), (100, y * 10))
        line.rgb = (50, y * 20, 50)  # set true color as RGB tuple
        # IMPORTANT: as you see it is not in the line.dxf namespace!
    # getting RGB values by r, g, b = line.rgb also works
    dwg.saveas("true_color_lines.dxf")


def rect(x, y, width=10, height=10):
    return (x, y), (x + width, y), (x, y + height), (x + width, y + height)


def solids_with_true_color():
    dwg = ezdxf.new('AC1018')  # for true color and transparency is DXF version AC1018 (ACAD R2004) or newer necessary
    msp = dwg.modelspace()
    for i in range(10):
        x = i * 7
        y = i * 7
        solid = msp.add_solid(rect(x, y))
        solid.rgb = (50, i * 20, 50)  # set true color as RGB tuple
        # IMPORTANT: as you see it is not in the solid.dxf namespace!
    dwg.saveas("true_color_solids.dxf")


def solids_with_transparency():
    dwg = ezdxf.new('AC1018')  # for true color and transparency is DXF version AC1018 (ACAD R2004) or newer necessary
    msp = dwg.modelspace()
    for i in range(10):
        x = i * 7
        y = i * 7
        solid = msp.add_solid(rect(x, y, 20, 20))
        solid.transparency = i / 10.  # set transparency as float between 0.0 (opaque) and 1.0 (100% transparent)
        # transparency: 0.0, 0.1, 0.2, ...
        # IMPORTANT: as you see it is not in the sold.dxf namespace and better never use the raw DXF data for transparency
    dwg.saveas("transparent_solids.dxf")


lwpolyline_with_true_color()
lines_with_true_color()
solids_with_true_color()
solids_with_transparency()
