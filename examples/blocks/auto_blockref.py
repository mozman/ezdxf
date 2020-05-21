# Purpose: 'flag' example
# Created: 04.11.2010
# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import random
from pathlib import Path
import ezdxf

DIR = Path('~/Desktop/Outbox').expanduser()


def get_random_point():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


SAMPLE_COORDS = [get_random_point() for x in range(50)]

flag_symbol = [(0, 0), (0, 5), (4, 3), (0, 3)]

doc = ezdxf.new('R2007')
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
for number, point in enumerate(SAMPLE_COORDS):
    values = {
        'NAME': f"P({number + 1})",
        'XPOS': f"x = {point[0]:.3f}",
        'YPOS': f"y = {point[1]:.3f}",
    }
    randomscale = 0.5 + random.random() * 2.0
    modelspace.add_auto_blockref('FLAG', point, values, dxfattribs={
        'layer': 'FLAGS',
        'rotation': -15
    }).set_scale(randomscale)

doc.set_modelspace_vport(height=200)
filename = DIR/'auto_flags.dxf'
doc.saveas(filename)
print("drawing '%s' created.\n" % filename)
