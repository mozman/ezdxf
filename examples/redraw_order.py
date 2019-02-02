# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import random
import ezdxf
from ezdxf.ezmath import Vector
from ezdxf.lldxf.const import SortEntities


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
    # AutoCAD regenerates entities in ascending handle order.
    # Change redraw order for DXF entities by assigning an sort handle to an objects handle
    # The sort handle can be any handle you want, even '0', but this sort handle will be drawn as latest (on top of all
    # other entities) and not as first as expected.
    #
    # just use color as sort handle, '%X': uppercase hex-value without 0x prefix, like 'FF'
    msp.set_redraw_order(
        (solid.dxf.handle, '%X' % solid.dxf.color) for solid in msp.query('SOLID')
    )


def reverse_order_solids_by_color(msp):
    msp.set_redraw_order(
        (solid.dxf.handle, '%X' % (10-solid.dxf.color)) for solid in msp.query('SOLID')
    )


def move_solids_on_top(msp, color, sort_handle='FFFF'):
    # This also works if a redraw order is already set
    order = dict(msp.get_redraw_order())  # returns a list of [(object_handle, sort_handle), ...] -> dict
    for solid in msp.query('SOLID[color=={}]'.format(color)):
        order[solid.dxf.handle] = sort_handle
    msp.set_redraw_order(order)  # accepts also a dict


def remove_solids(msp, color=6):
    for solid in msp.query('SOLID[color=={}]'.format(color)):
        msp.delete_entity(solid)


def run():
    dwg = ezdxf.new('R2004')  # does not work with AC1015/R2000, but it should
    dwg.header['$SORTENTS'] = SortEntities.REGEN
    msp = dwg.modelspace()

    add_solids(msp, count=1000, min_size=3, max_size=7)
    dwg.saveas('sort_solids_unordered.dxf')
    order_solids_by_color(msp)  # 1 -> 7
    dwg.saveas('sort_solids_ordered.dxf')
    reverse_order_solids_by_color(msp)  # 7 -> 1
    dwg.saveas('sort_solids_reversed_ordered.dxf')
    move_solids_on_top(msp, 6)  # 7, 5, 4, 3, 2, 1, 6
    dwg.saveas('sort_solids_6_on_top.dxf')  # 6 is magenta
    # AutoCAD has no problem with removed entities in the redraw order table (SORTENTSTABLE)
    remove_solids(msp, 6)
    dwg.saveas('sort_solids_removed_color_6.dxf')


if __name__ == '__main__':
    run()
