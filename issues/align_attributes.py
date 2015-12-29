# Issue reported by Gustavo Meira

import ezdxf

dwg = ezdxf.new('AC1024')
modelspace = dwg.modelspace()

block = dwg.blocks.new('TEST')


block.add_lwpolyline([(0,0), (0, 1), (1, 1), (1, 0), (0,0)])

blockref = modelspace.add_blockref('TEST', (-3, -3))
modelspace.add_circle((-3, -1), 0.1, dxfattribs={'color': 3})

blockref.add_attrib("TAG1", "TEXT1", (-3, -1))
tag1 = blockref.get_attrib('TAG1')
tag1.set_pos((-3, -1), align='MIDDLE_CENTER')

dwg.saveas("align_attributes.dxf")

