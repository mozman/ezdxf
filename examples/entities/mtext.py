# Created: 11.08.2013
# Copyright (c) 2013-2019 Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new('R2007')
msp = doc.modelspace()
attribs = {
    'char_height': 0.7,
    'width': 5.0,
}
msp.add_line((-10, -1), (10, -2))
mtext = msp.add_mtext("This is a long MTEXT line with line wrapping!", attribs)
mtext.set_bg_color((108, 204, 193))

filename = 'mtext.dxf'
doc.saveas(filename)
print("drawing '%s' created.\n" % filename)
