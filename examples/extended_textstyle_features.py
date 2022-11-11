# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

doc = ezdxf.new()
doc.styles.add("Arial", font="Arial.ttf")
text_style = doc.styles.add("ArialItalic", font="Arial.ttf")
text_style.set_extended_font_data(family='Arial', italic=True, bold=False)
text_style = doc.styles.add("ArialBold", font="Arial.ttf")
text_style.set_extended_font_data(family='Arial', italic=False, bold=True)
text_style = doc.styles.add("ArialItalicBold", font="Arial.ttf")
text_style.set_extended_font_data(family='Arial', italic=True, bold=True)

msp = doc.modelspace()
msp.add_text("Arial", dxfattribs={"style": "Arial"}).set_placement((0, 0))
msp.add_text("Arial Italic", dxfattribs={"style": "ArialItalic"}).set_placement((0, 5))
msp.add_text("Arial Bold", dxfattribs={"style": "ArialBold"}).set_placement((0, 10))
msp.add_text("Arial Italic Bold", dxfattribs={"style": "ArialItalicBold"}).set_placement((0, 15))

doc.set_modelspace_vport(25, center=(10, 7.5))
doc.saveas(CWD / "extended_textstyle_features.dxf")
