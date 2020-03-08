import ezdxf
from ezdxf.math import Vector

DXFFILE = 'drainage.dxf'
OUTFILE = r'C:\Users\manfred\Desktop\Outbox\encircle.dxf'

dwg = ezdxf.readfile(DXFFILE)
msp = dwg.modelspace()
dwg.layers.new(name='MyCircles', dxfattribs={'color': 4})


def get_first_circle_center(block_layout):
    block = block_layout.block
    base_point = Vector(block.dxf.base_point)
    circles = block_layout.query('CIRCLE')
    if len(circles):
        circle = circles[0]  # take first circle
        center = circle.dxf.center
        return center - base_point
    else:
        return Vector(0, 0, 0)


# block definition to examine
block_layout = dwg.blocks.get('WB')
offset = get_first_circle_center(block_layout)

for e in msp.query('INSERT[name=="WB"]'):
    print("INSERT {e.dxf.name}\n location: {e.dxf.insert}\n layer: {e.dxf.layer}\n extrusion: {e.dxf.extrusion}\n".format(e=e))
    scale = e.get_dxf_attrib('xscale', 1)  # assume uniform scaling
    angle = e.get_dxf_attrib('rotation', 0)
    location = e.dxf.insert + (offset * scale).rotate_deg(angle)
    msp.add_circle(center=location, radius=1, dxfattribs={'layer': 'MyCircles'})

dwg.saveas(OUTFILE)
# saving produces unreadable file, also without adding anything



