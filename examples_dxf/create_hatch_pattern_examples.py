#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import ezdxf
from ezdxf.tools import pattern
from ezdxf.render.forms import square, translate

HEIGHT = 300


def add_predefined_hatch_pattern(msp, cols, size, gap, scale):
    for index, name in enumerate(pattern.ISO_PATTERN.keys()):
        x = (index % cols) * (size + gap)
        y = (index // cols) * (size + gap)
        boundary = list(translate(square(size), (x, HEIGHT - y)))
        msp.add_lwpolyline(
            boundary,
            close=True,
            dxfattribs={'layer': 'LINE'}
        )
        hatch = msp.add_hatch(dxfattribs={'layer': 'HATCH'})
        hatch.set_pattern_fill(name=name, scale=scale)
        hatch.paths.add_polyline_path(boundary, is_closed=True)


if __name__ == '__main__':
    # Imperial: Inch
    doc = ezdxf.new(units=1)
    add_predefined_hatch_pattern(
        doc.modelspace(), cols=10, size=10, gap=1, scale=4)
    doc.set_modelspace_vport(HEIGHT, (30, HEIGHT / 2))
    doc.saveas('hatch_pattern_imperial.dxf')

    # ISO: Meter
    doc = ezdxf.new(units=6)
    add_predefined_hatch_pattern(
        doc.modelspace(), cols=10, size=10, gap=1, scale=0.25)
    doc.set_modelspace_vport(HEIGHT, (30, HEIGHT / 2))
    doc.saveas('hatch_pattern_iso.dxf')
