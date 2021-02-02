from pathlib import Path
import ezdxf
from ezdxf.addons import text2path

DIR = Path('~/Desktop/Outbox').expanduser()
doc = ezdxf.new()
doc.styles.new('FONT', dxfattribs={'font': "arialn.ttf"})
msp = doc.modelspace()

text = msp.add_text("Arial Narrow", dxfattribs={
    'style': 'FONT',
    'layer': 'TEXT',
    'height': 1.0,
    'color': 1,
})

attr = {'layer': 'OUTLINE', 'color': 2}
segments = 4
for path in text2path.make_paths_from_entity(text):
    msp.add_lwpolyline(path.flattening(1, segments=segments), dxfattribs=attr)

doc.set_modelspace_vport(3, (2, 0))
doc.saveas(DIR / 'entity2path.dxf')
