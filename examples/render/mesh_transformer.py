# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.render.forms import cube

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

mycube = cube().scale_uniform(10).subdivide(2)
mycube.render(msp)

doc.saveas(DIR / 'subdivided_cube.dxf')
