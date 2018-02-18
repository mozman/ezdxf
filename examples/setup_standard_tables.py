# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.tools import standards


def main():
    dwg = ezdxf.new('R12')
    for name, desc, pattern in standards.linetypes():
        if name in dwg.linetypes:
            continue
        dwg.linetypes.new(name, dxfattribs={
            'description': desc,
            'pattern': pattern,
        })
    for name, font in standards.styles():
        if name in dwg.styles:
            continue
        dwg.styles.new(name, dxfattribs={
            'font': font,
        })

    msp = dwg.modelspace()
    for n, ltype in enumerate(dwg.linetypes):
        name = ltype.dxf.name
        msp.add_line((0, n), (10, n), dxfattribs={'linetype': name})
        msp.add_text(name, dxfattribs={
            'insert': (0, n + 0.1),
            'height': 0.25,
            'style': 'ARIAL'
        })
    dwg.saveas('standard_linetypes.dxf')


if __name__ == '__main__':
    main()
