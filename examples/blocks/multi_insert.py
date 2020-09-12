# Created: 04.08.2020
# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import random
from pathlib import Path
import ezdxf

DIR = Path('~/Desktop/Outbox').expanduser()

flag_symbol = [(0, 0), (0, 5), (4, 3), (0, 3)]

doc = ezdxf.new()
doc.layers.new('FLAGS')

# first create a block
flag = doc.blocks.new(name='FLAG')

# add dxf entities to the block (the flag)
# use base_point = (x, y) to define an other base_point than (0, 0)
flag.add_polyline2d(flag_symbol)
flag.add_circle((0, 0), .4, dxfattribs={'color': 1})

# define some attributes
flag.add_attdef('NAME', (0.5, -0.5), dxfattribs={'height': 0.5, 'color': 3})
flag.add_attdef('XPOS', (0.5, -1.0), dxfattribs={'height': 0.25, 'color': 4})
flag.add_attdef('YPOS', (0.5, -1.5), dxfattribs={'height': 0.25, 'color': 4})
modelspace = doc.modelspace()
location = (0, 0)
values = {
    'NAME': "Flag",
    'XPOS': f"x = {location[0]:.3f}",
    'YPOS': f"y = {location[1]:.3f}",
}

block_ref = modelspace.add_blockref('FLAG', location, dxfattribs={
    'layer': 'FLAGS',
}).grid(size=(5, 5), spacing=(10, 10))
block_ref.dxf.rotation = 15
block_ref.add_auto_attribs(values)

filename = DIR / 'multi_insert_with_attribs.dxf'
doc.set_modelspace_vport(height=200)
doc.saveas(filename)
print("drawing '%s' created.\n" % filename)
