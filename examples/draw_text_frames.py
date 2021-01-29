from pathlib import Path
import ezdxf
from ezdxf import disassemble, options

options.use_matplotlib_font_support = True

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.readfile(Path(__file__).parent / '../examples_dxf/text_fonts.dxf')
msp = doc.modelspace()

# required to switch layer on/off
doc.layers.new('TEXT_FRAME', dxfattribs={'color': 6})
for frame in disassemble.to_primitives(msp.query('TEXT')):
    msp.add_lwpolyline(frame.vertices(), close=True,
                       dxfattribs={'layer': 'TEXT_FRAME'})


doc.saveas(DIR / 'text_frames.dxf')
