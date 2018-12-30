# coding: utf8
import ezdxf

dwg = ezdxf.new('AC1018')
msp = dwg.modelspace()

#   Blockname 'PUNKTKENNZEICHEN'
block_punkt = dwg.blocks.new(name='NUMPUNKT')
#   Kreis um Einfuegepunkt (default: 0,0) mit Radius 0.03
block_punkt.add_circle((0, 0, 0), 0.03)

block_punkt.add_attdef('TEXT', (0, 0, 0), {'height': 0.07})
block_punkt.add_attdef('HOEHE', (0, 0, 0), {'height': 0.04})
block_punkt.add_attdef('BEMERKUNG', (0, 0, 0), {'height': 0.04})

p = (10, 10, 10)
blockref = msp.add_blockref('NUMPUNKT', p, dxfattribs={'layer': 'TestAttrib3D'})

x, y, z = p
blockref.add_attrib(tag="TEXT", text="Text", insert=(x+0.05, y+0.05, z),  dxfattribs={'height': 0.07, 'extrusion': (0, -1, 0)})
blockref.add_attrib(tag="HOEHE", text="Höhe", insert=(x+0.05, y, z), dxfattribs={'height': 0.04, 'extrusion': (0, -1, 0)})
blockref.add_attrib(tag="BEMERKUNG", text="Bemerkung", insert=(x+0.05, y-0.05, z), dxfattribs={'height': 0.04, 'extrusion': (0, -1, 0)})

dwg.saveas('attrib3d.dxf')
