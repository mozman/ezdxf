# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import random
import ezdxf
from ezdxf.algebra import Vector


def random_in_range(a, b):
    return random.random() * float(b-a) + a


def random_pos(lower_left=(0, 0), upper_right=(100, 100)):
    x0, y0 = lower_left
    x1, y1 = upper_right
    x = random_in_range(x0, x1)
    y = random_in_range(y0, y1)
    return Vector(x, y)


def add_solids(msp, count=20, min_size=1, max_size=5, color=None, layer='SOLIDS'):
    def add_solid(pos, size, dxfattribs):
        points = [
            pos,
            pos + (size, 0),
            pos + (0, size),
            pos + (size, size),
        ]
        msp.add_solid(points, dxfattribs=dxfattribs)

    dxfattribs = {
        'color': color,
        'layer': layer,
    }
    for _ in range(count):
        pos = random_pos((0, 0), (100, 100))
        size = random_in_range(min_size, max_size)
        if color is None:
            dxfattribs['color'] = random.randint(1, 7)
            dxfattribs['layer'] = 'color_'+str(dxfattribs['color'])
        add_solid(pos, size, dxfattribs)


def order_solids_by_color(msp):
    solids = msp.query('SOLID')
    sorted_solids = sorted(solids, key=lambda e: e.dxf.color)
    # just use color as sort handle
    redraw_order = [(solid.dxf.handle, str(solid.dxf.color)) for solid in sorted_solids]
    msp.set_redraw_order(redraw_order)


def run():
    dwg = ezdxf.new('R2004')
    dwg.header['$SORTENTS'] = 16  # Sorts for REGEN commands
    msp = dwg.modelspace()

    add_solids(msp, count=1000, min_size=3, max_size=7)
    dwg.saveas('colored_solids_unordered.dxf')
    order_solids_by_color(msp)
    dwg.saveas('colored_solids_ordered.dxf')


if __name__ == '__main__':
    run()
