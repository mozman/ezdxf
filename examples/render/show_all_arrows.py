# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

import ezdxf

dwg = ezdxf.new('R12', setup=True)
msp = dwg.modelspace()

for index, name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
    if name == "":
        label = '"" = closed filled'
    else:
        label = name
    y = index * 2
    msp.add_text(label, {'style': 'OpenSans', 'height': .25}).set_pos((-5, y - .5))
    msp.add_line((-5, y), (-1, y))
    msp.add_line((5, y), (10, y))
    cp1 = msp.add_arrow(name, insert=(0, y), size=1, rotation=0)
    cp2 = msp.add_arrow(name, insert=(4, y), size=1, rotation=0, reverse=True)
    msp.add_line(cp1, cp2)
    msp.add_arrow_blockref(name, insert=(7, y), size=.3, rotation=45)
    msp.add_arrow_blockref(name, insert=(7.5, y), size=.3, rotation=135)
    msp.add_arrow_blockref(name, insert=(8, y), size=.5, rotation=-90)

msp.add_line((0, 0), (0, y))
msp.add_line((4, 0), (4, y))
msp.add_line((8, 0), (8, y))

dwg.saveas('all_arrows.dxf')
