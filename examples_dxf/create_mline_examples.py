#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.lldxf import const
from ezdxf.math import Shape2d

OUTBOX = Path('~/Desktop/Outbox').expanduser()
if not OUTBOX.exists():
    OUTBOX = Path('.')


def add_top_zero_bottom_mlines(msp, vertices, closed: bool = False,
                               style: str = 'Standard'):
    shape = Shape2d(vertices)
    msp.add_mline(shape.vertices, dxfattribs={
        'style_name': style,
        'justification': const.MLINE_BOTTOM,
        'closed': closed,
    })
    shape.translate((0, 20, 0))
    msp.add_mline(shape.vertices, dxfattribs={
        'style_name': style,
        'justification': const.MLINE_ZERO,
        'closed': closed,
    })
    shape.translate((0, 20, 0))
    msp.add_mline(shape.vertices, dxfattribs={
        'style_name': style,
        'justification': const.MLINE_TOP,
        'closed': closed,
    })


def create_simple_mline(style='Standard'):
    doc = ezdxf.new()
    setup_styles(doc)
    msp = doc.modelspace()
    add_top_zero_bottom_mlines(msp, [(0, 0), (10, 0)], style=style)
    doc.set_modelspace_vport(60, center=(10, 30))
    doc.saveas(OUTBOX / f'mline_1_seg_{style}.dxf')


def create_3seg_mline(style='Standard'):
    doc = ezdxf.new()
    setup_styles(doc)
    msp = doc.modelspace()
    add_top_zero_bottom_mlines(msp, [(0, 0), (10, 0), (15, 5), (15, 10)],
                               style=style)
    doc.set_modelspace_vport(60, center=(10, 30))
    doc.saveas(OUTBOX / f'mline_3_seg_{style}.dxf')


def create_square_mline(style='Standard'):
    doc = ezdxf.new()
    setup_styles(doc)
    msp = doc.modelspace()
    add_top_zero_bottom_mlines(msp, [(0, 0), (10, 0), (10, 10), (0, 10)],
                               closed=True, style=style)
    doc.set_modelspace_vport(60, center=(10, 30))
    doc.saveas(OUTBOX / f'mline_square_{style}.dxf')


def setup_styles(doc):
    style = doc.mline_styles.new('above')
    style.elements.append(0.5, 1)
    style.elements.append(0.25, 3)
    style = doc.mline_styles.new('below')
    style.elements.append(-0.5, 2)
    style.elements.append(-0.25, 4)
    style = doc.mline_styles.new('angle')
    style.dxf.start_angle = 45
    style.dxf.end_angle = 45
    style.elements.append(0.5, 6)
    style.elements.append(-0.5, 5)


if __name__ == '__main__':
    for style in ('Standard', 'above', 'below', 'angle'):
        create_simple_mline(style)
        create_3seg_mline(style)
        create_square_mline(style)
