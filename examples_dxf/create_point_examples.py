# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.render import point


def new_doc(pdmode: int, pdsize: float = 1):
    doc = ezdxf.new('R2000')
    doc.header['$PDMODE'] = pdmode
    doc.header['$PDSIZE'] = pdsize
    return doc


PDSIZE = 0.5
MODES = [
    0, 1, 2, 3, 4,
    32, 33, 34, 35, 36,
    64, 65, 66, 67, 68,
    96, 97, 98, 99, 100,
]


def add_point(x, angle: float, color: int):
    pnt = msp.add_point((x, 3), dxfattribs={
        'color': color,
        'angle': angle,
    })
    for entity in [e.translate(0, -2, 0) for e in
                   point.virtual_entities(pnt, PDSIZE, pdmode)]:
        msp.add_entity(entity)


for pdmode in MODES:
    doc = new_doc(pdmode, PDSIZE)
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (10, 0), (10, 4), (0, 4)], dxfattribs={
        'closed': True,
    })
    add_point(1, 0, 1)
    add_point(3, 30, 2)
    add_point(5, 45, 3)
    add_point(7, 60, 4)
    add_point(9, 90, 6)
    doc.set_modelspace_vport(10, (5, 2))
    doc.saveas(f'points_pdmode_{pdmode}.dxf')
