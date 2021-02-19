# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons import text2path
from ezdxf import zoom
from ezdxf.lldxf import const
EXAMPLES = Path(__file__).parent.parent.parent / 'examples_dxf'


OUTBOX = Path('~/Desktop/Outbox').expanduser()
doc = ezdxf.readfile(EXAMPLES / "text_mirror_true_type_font.dxf")
doc.layers.new('OUTLINE', dxfattribs={'color': 1})
msp = doc.modelspace()
zoom.extents(msp, factor=1.1)

kind = text2path.Kind.SPLINES
for text in msp.query('TEXT'):
    for e in text2path.virtual_entities(text, kind=kind):
        e.dxf.layer = 'OUTLINE'
        e.dxf.color = const.BYLAYER
        msp.add_entity(e)

doc.saveas(OUTBOX / 'mirror_text.dxf')
