# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from pathlib import Path

import ezdxf
from ezdxf.tools.standards import styles

DIR = Path("~/Desktop/Outbox").expanduser()
doc = ezdxf.new("R12", setup=True)
msp = doc.modelspace()

y = 0
height = 0.5
line_height = 1.5
for style, font in styles():
    msp.add_text(style, {"style": style, "height": height}).set_pos((0, y))
    y += height * line_height

doc.saveas(DIR / "using_all_text_styles.dxf")
