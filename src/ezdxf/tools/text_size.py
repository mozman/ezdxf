#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Tuple
from dataclasses import dataclass
import ezdxf
from ezdxf.entities import Text, MText, get_font_name
from ezdxf.tools.fonts import make_font, MonospaceFont, AbstractFont

__all__ = ["text_size", "mtext_size", "TextSize", "MTextSize"]


@dataclass(frozen=True)
class TextSize:
    width: float
    # The text entity has a fixed font:
    cap_height: float  # height of "X" without descender
    total_height: float  # including the descender


@dataclass(frozen=True)
class MTextSize:
    total_width: float
    total_height: float
    columns: Tuple[float, ...]
    gutter_width: float
    # Storing additional font metrics like "cap_height" makes no sense, because
    # the font metrics can be variable by using inline codes to vary the text
    # height or the width factor or even changing the used font at all.


def text_size(text: Text) -> TextSize:
    """Returns the measured text width and the font cap-height and total-height
    for a :class:`~ezdxf.entities.Text` entity.
    This function uses the `Matplotlib` support (if available) to measure the
    final rendering size for the :class:`Text` entity as close as
    possible. This function does not measure the real char height!
    """
    width_factor: float = text.dxf.get_default("width")
    text_width: float = 0.
    cap_height: float = text.dxf.get_default("height")
    font: AbstractFont = MonospaceFont(cap_height, width_factor)
    if ezdxf.options.use_matplotlib and text.doc is not None:
        style = text.doc.styles.get(text.dxf.get_default("style"))
        font_name = get_font_name(style)
        font = make_font(font_name, cap_height, width_factor)

    total_height = font.measurements.total_height
    content = text.plain_text()
    if content:
        text_width = font.text_width(content)
    return TextSize(text_width, cap_height, total_height)


def mtext_size(mtext: MText) -> MTextSize:
    """Returns the text width and height and columns information for a
    :class:`~ezdxf.entities.MText` entity.
    This function uses the `Matplotlib` support (if available) and the text
    layout engine to determine the final rendering size for the :class:`MText`
    entity as close as possible. Because of the requirement of building the full
    layout this function is slow!

    """
    pass
