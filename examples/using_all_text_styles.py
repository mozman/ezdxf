# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.tools.standards import styles
doc = ezdxf.new('R12', setup=True)
msp = doc.modelspace()

y = 0
height = .5
line_height = 1.5
for style, font in styles():
    msp.add_text(style, {'style': style, 'height': height}).set_pos((0, y))
    y += height * line_height

doc.saveas('using_all_text_styles.dxf')
