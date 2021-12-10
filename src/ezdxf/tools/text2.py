#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
"""
Like the ezdxf.tools.text module but this tools can have dependencies on DXF
entities!

Nonetheless keep real imports as small as possible to avoid unnecessary
circular import errors.

"""

from typing import TYPE_CHECKING, Tuple, List
import math
from ezdxf import const
from ezdxf.tools import fonts
from ezdxf.tools.text import leading

if TYPE_CHECKING:
    from ezdxf.entities import MText


def estimate_mtext_extents(mtext: "MText") -> Tuple[float, float]:
    """Estimate the width and height for a single column
    :class:`~ezdxf.entities.MText` entity.

    This function is faster than the :func:`mtext_size` function, but the
    result is very inaccurate if inline codes are used or auto line wrapping
    is involved!

    This function uses the optional `Matplotlib` package if available.

    Returns:
        Tuple[width, height]

    """

    def make_font():
        doc = mtext.doc
        if doc:
            style = doc.styles.get(mtext.dxf.get_default("style"))
            if style is not None:
                return style.make_font(cap_height)  # type: ignore
        return fonts.make_font(const.DEFAULT_TTF, cap_height=cap_height)

    def estimate_line_wraps(_width: float) -> int:
        """Does not care about spaces for line breaks!"""
        if has_column_width:
            return math.ceil(_width / column_width)
        return 1

    max_width: float = 0.0
    height: float = 0.0

    column_width: float = mtext.dxf.get("width", 0.0)
    cap_height: float = mtext.dxf.get_default("char_height")
    line_spacing_factor: float = mtext.dxf.get_default("line_spacing_factor")

    has_column_width: bool = column_width > 0.0
    content: List[str] = mtext.plain_text(split=True, fast=True)  # type: ignore
    line_count: int = len(content)

    if (line_count > 0) and (line_count > 1 or content[0] != ""):
        line_count = 0
        font = make_font()
        for line in content:
            line_width = font.text_width(line)
            line_count += estimate_line_wraps(line_width)

            # Note: max_width can be smaller than the column_width, if all lines
            # are shorter than column_width!
            if has_column_width and line_width > column_width:
                line_width = column_width
            max_width = max(max_width, line_width)

        spacing = leading(cap_height, line_spacing_factor) - cap_height
        height = cap_height * line_count + spacing * (line_count - 1)

    return max_width, height
