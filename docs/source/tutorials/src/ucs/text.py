# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from pathlib import Path
OUT_DIR = Path('~/Desktop/Outbox').expanduser()

import math
import ezdxf
from ezdxf.math import UCS

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# thickness for text works only with shx fonts not with true type fonts
doc.styles.new('TXT', dxfattribs={'font': 'romans.shx'})

ucs = UCS(origin=(0, 2, 2)).rotate_local_x(math.radians(-45))
text = msp.add_text(
    text="TEXT",
    dxfattribs={
        # text rotation angle in degrees in UCS
        'rotation': -45,
        'thickness': .333,
        'color': 1,
        'style': 'TXT',
    }
)
# set text position in UCS
text.set_pos((0, 0, 0), align='MIDDLE_CENTER')
text.transform_to_wcs(ucs)

ucs.render_axis(msp)
doc.saveas(OUT_DIR / 'ucs_text.dxf')
