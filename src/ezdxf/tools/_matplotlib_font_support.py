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


def get_font(font_name: str) -> fonts.Font:
    font_name = fonts.resolve_shx_font_name(font_name)
    return fonts.get(font_name)


@lru_cache(maxsize=256)
def get_font_properties(font: fonts.Font) -> FontProperties:
    font_properties = text_renderer.default_font
    if font:
        try:
            font_properties = FontProperties(
                family=font.family,
                style=font.style,
                stretch=font.stretch,
                weight=font.weight,
            )
        except ValueError:
            pass
    return font_properties
