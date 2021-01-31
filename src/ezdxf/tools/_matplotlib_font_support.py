# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from functools import lru_cache
from ezdxf import options
from ezdxf.addons.drawing.matplotlib import TextRenderer
from matplotlib.font_manager import FontProperties
from . import fonts

text_renderer = TextRenderer(FontProperties(), use_cache=False)

# Setup fonts - this is not done automatically, because this may take a long
# time and is not important for every user.
# Load default font definitions, included in ezdxf:
fonts.load()

# Add font definitions available at the running system:
if options.load_system_fonts:
    fonts.add_system_fonts()


@lru_cache(maxsize=256)
def get_font_properties(font_face: fonts.FontFace) -> FontProperties:
    font_properties = text_renderer.default_font
    if font_face:
        try:
            font_properties = FontProperties(
                family=font_face.family,
                style=font_face.style,
                stretch=font_face.stretch,
                weight=font_face.weight,
            )
        except ValueError:
            pass
    return font_properties
