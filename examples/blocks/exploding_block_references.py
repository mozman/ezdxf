# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from typing import cast
from pathlib import Path
import ezdxf

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new('R2010')
msp = doc.modelspace()

block = doc.blocks.new(name='TEST')
block.add_lwpolyline([(0, 0), (1, 0), (1, 1), (0, 1)], dxfattribs={'closed': True, 'color': 3})
block.add_circle((0.5, 0.5), 0.5, dxfattribs={'color': 1})
block.add_text('TEST', dxfattribs={'height': 0.1, 'color': 5, 'rotation': 45}).set_pos((0.5, 0.5),
                                                                                       align='MIDDLE_CENTER')
block.add_spline(fit_points=[(0, 0), (.4, .3), (.6, .7), (1, 1)])
block.add_ellipse(center=(0.5, 0.5), major_axis=(0.5, 0.5), ratio=0.5, dxfattribs={'color': 5})
block.add_lwpolyline([(0, 1.1), (0.3, 1.1, -0.5), (.7, 1.1), (1, 1.1)], format='xyb', dxfattribs={'color': 6})

# horizontal
msp.add_blockref('TEST', (0, 0))
msp.add_blockref('TEST', (2, 0)).set_scale(2)
msp.add_blockref('TEST', (5, 0), dxfattribs={'xscale': 2})  # none uniform scaling

# rotated 45 degrees
msp.add_blockref('TEST', (0, 3), dxfattribs={'rotation': 45})
msp.add_blockref('TEST', (2, 3), dxfattribs={'rotation': 45}).set_scale(2)
msp.add_blockref('TEST', (5, 3), dxfattribs={'xscale': 2, 'rotation': 45})  # none uniform scaling

doc.set_modelspace_vport(4, center=(3, 3))
doc.saveas(DIR / 'scaling.dxf')

# Explode flag block references
for block in msp.query("INSERT[name=='TEST']"):
    cast('Insert', block).explode(non_uniform_scaling=True)

doc.saveas(DIR / 'exploded.dxf')
