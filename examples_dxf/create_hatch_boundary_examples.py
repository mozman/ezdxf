#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import List, Optional
import ezdxf
from ezdxf.math import Shape2d
from ezdxf.render.forms import square
from ezdxf.lldxf import const

DX = 11
SIZE = 10


def add_hatch(msp, external: List[Shape2d] = None,
              *,
              outermost: List[Shape2d] = None,
              default: List[Shape2d] = None,
              hatch_style=const.HATCH_STYLE_NESTED,
              offset=(0, 0),
              ):
    def add(path, flags: int, color: int, layer: str):
        path.translate(offset)
        hatch.paths.add_polyline_path(
            path.vertices, flags=flags)
        msp.add_lwpolyline(path.vertices, dxfattribs={
            'color': color, 'layer': layer, 'closed': True})

    hatch = msp.add_hatch(2, dxfattribs={'layer': 'HATCH'})
    hatch.dxf.hatch_style = hatch_style
    if external:
        for path in external:
            add(path.copy(), const.BOUNDARY_PATH_EXTERNAL, 1, 'EXTERNAL-PATH')
    if outermost:
        for path in outermost:
            add(path.copy(), const.BOUNDARY_PATH_OUTERMOST, 3, 'OUTERMOST-PATH')
    if default:
        for path in default:
            add(path.copy(), const.BOUNDARY_PATH_DEFAULT, 5, 'DEFAULT-PATH')


def add_hatch_boundaries_test(msp, offset):
    x, y = offset
    external = Shape2d(square(SIZE))
    outermost = Shape2d(square(SIZE - 2))
    outermost.translate((1, 1))
    default0 = Shape2d(square(SIZE - 4))
    default0.translate((2, 2))
    default1 = Shape2d(square(SIZE - 6))
    default1.translate((3, 3))
    add_hatch(msp, external=None,
              outermost=None,
              default=[external, outermost, default0, default1],
              hatch_style=const.HATCH_STYLE_NESTED,
              offset=offset,
              )
    add_hatch(msp, external=[default0, default1],
              outermost=[external, outermost],
              hatch_style=const.HATCH_STYLE_OUTERMOST,
              offset=(x + DX, y)
              )
    add_hatch(msp, external=[external, outermost, default0, default1],
              hatch_style=const.HATCH_STYLE_IGNORE,
              offset=(x + DX + DX, y)
              )


def add_hatch_boundaries_adjacent(msp, offset):
    x, y = offset
    external = Shape2d(square(SIZE))
    outermost = Shape2d(square(SIZE - 2))
    outermost.translate((1, 1))
    default0 = Shape2d(square(2))
    default0.translate((2, 2))
    default1 = Shape2d(square(2))
    default1.translate((6, 2))
    add_hatch(msp, external=[external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_NESTED,
              offset=offset,
              )
    add_hatch(msp, external=[external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_OUTERMOST,
              offset=(x + DX, y)
              )
    add_hatch(msp, external=[external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_IGNORE,
              offset=(x + DX + DX, y)
              )


def add_hatch_boundaries_overlapping(msp, offset):
    x, y = offset
    external = Shape2d(square(SIZE))
    outermost = Shape2d(square(SIZE - 2))
    outermost.translate((1, 1))
    default0 = Shape2d(square(3))
    default0.translate((2, 2))
    default1 = Shape2d(square(3))
    default1.translate((4, 3))
    add_hatch(msp, external=[external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_NESTED,
              offset=offset,
              )
    add_hatch(msp, external=[external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_OUTERMOST,
              offset=(x + DX, y)
              )
    add_hatch(msp, external=[external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_IGNORE,
              offset=(x + DX + DX, y)
              )


def add_hatch_boundaries_nested(msp, offset):
    x, y = offset
    external = Shape2d(square(SIZE))
    outermost = Shape2d(square(SIZE - 2))
    outermost.translate((1, 1))
    default0 = Shape2d(square(SIZE - 4))
    default0.translate((2, 2))
    default1 = Shape2d(square(SIZE - 6))
    default1.translate((3, 3))
    add_hatch(msp, [external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_NESTED,
              offset=offset,
              )
    add_hatch(msp, [external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_OUTERMOST,
              offset=(x + DX, y)
              )
    add_hatch(msp, [external],
              outermost=[outermost],
              default=[default0, default1],
              hatch_style=const.HATCH_STYLE_IGNORE,
              offset=(x + DX + DX, y)
              )


if __name__ == '__main__':
    doc = ezdxf.new()
    add_hatch_boundaries_nested(doc.modelspace(), offset=(0, 0))
    add_hatch_boundaries_adjacent(doc.modelspace(), offset=(0, 11))
    add_hatch_boundaries_overlapping(doc.modelspace(), offset=(0, 22))
    doc.set_modelspace_vport(40, (15, 20))
    doc.saveas('hatch_boundaries.dxf')
