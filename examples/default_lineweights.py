# Purpose: using true color and transparency
# Created: 05.09.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.lldxf.const import VALID_DXF_LINEWEIGHTS

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()
for index, weight in enumerate(VALID_DXF_LINEWEIGHTS):
    y = index
    msp.add_line((0, y), (10, y), dxfattribs={'lineweight': weight})
    msp.add_text(f'Lineweight: {weight / 100.0:0.2f}', dxfattribs={'height': 0.18}).set_pos((0, y + 0.3))
doc.set_modelspace_vport(25, center=(5, 12.5))
doc.saveas(DIR / 'valid_lineweights.dxf')
