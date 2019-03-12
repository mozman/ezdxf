# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

import ezdxf

dwg = ezdxf.new('R2018', setup=True)
msp = dwg.modelspace()
y = 0

for index, name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
    if name == "":
        label = '"" = closed filled'
    else:
        label = name
    y = index * 2

    def add_connection_point(p):
        msp.add_circle(p, radius=0.01, dxfattribs={'color': 1})
    msp.add_text(label, {'style': 'OpenSans', 'height': .25}).set_pos((-5, y - .5))
    msp.add_line((-5, y), (-1, y))
    msp.add_line((5, y), (10, y))
    # left side |<- is the reverse orientation
    cp1 = msp.add_arrow(name, insert=(0, y), size=1, rotation=180, dxfattribs={'color': 7})
    # right side ->| is the base orientation
    cp2 = msp.add_arrow(name, insert=(4, y), size=1, rotation=0, dxfattribs={'color': 7})
    msp.add_line(cp1, cp2)
    add_connection_point(cp1)
    add_connection_point(cp2)

    add_connection_point(msp.add_arrow_blockref(name, insert=(7, y), size=.3, rotation=45))
    add_connection_point(msp.add_arrow_blockref(name, insert=(7.5, y), size=.3, rotation=135))
    add_connection_point(msp.add_arrow_blockref(name, insert=(8, y), size=.5, rotation=-90))


msp.add_line((0, 0), (0, y))
msp.add_line((4, 0), (4, y))
msp.add_line((8, 0), (8, y))

dwg.saveas('all_arrows_{}.dxf'.format(dwg.acad_release))
