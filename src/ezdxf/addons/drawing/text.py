# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import enum
import re
from math import radians
from typing import Union, Tuple, Dict, Iterable, List, Optional, Callable

import ezdxf.lldxf.const as DXFConstants
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.debug_utils import draw_rect
from ezdxf.addons.drawing import fonts
from ezdxf.entities import MText, Text, Attrib
from ezdxf.math import Matrix44, Vec3, sign

"""
Search google for 'typography' or 'font anatomy' for explanations of terms like 'baseline' and 'x-height'

A Visual Guide to the Anatomy of Typography: https://visme.co/blog/type-anatomy/
Anatomy of a Character: https://www.fonts.com/content/learning/fontology/level-1/type-anatomy/anatomy
"""


@enum.unique
class HAlignment(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


@enum.unique
class VAlignment(enum.Enum):
    TOP = 0  # the top of capital letters or letters with ascenders (like 'b')
    LOWER_CASE_CENTER = 1  # the midpoint between the baseline and the x-height
    BASELINE = 2  # the line which text rests on, characters with descenders (like 'p') are partially below this line
    BOTTOM = 3  # the lowest point on a character with a descender (like 'p')


Alignment = Tuple[HAlignment, VAlignment]
AnyText = Union[Text, MText, Attrib]

# multiple of cap_height between the baseline of the previous line and the baseline of the next line
DEFAULT_LINE_SPACING = 5 / 3

DXF_MTEXT_ALIGNMENT_TO_ALIGNMENT: Dict[int, Alignment] = {
    DXFConstants.MTEXT_TOP_LEFT: (HAlignment.LEFT, VAlignment.TOP),
    DXFConstants.MTEXT_TOP_CENTER: (HAlignment.CENTER, VAlignment.TOP),
    DXFConstants.MTEXT_TOP_RIGHT: (HAlignment.RIGHT, VAlignment.TOP),
    DXFConstants.MTEXT_MIDDLE_LEFT: (HAlignment.LEFT, VAlignment.LOWER_CASE_CENTER),
    DXFConstants.MTEXT_MIDDLE_CENTER: (HAlignment.CENTER, VAlignment.LOWER_CASE_CENTER),
    DXFConstants.MTEXT_MIDDLE_RIGHT: (HAlignment.RIGHT, VAlignment.LOWER_CASE_CENTER),
    DXFConstants.MTEXT_BOTTOM_LEFT: (HAlignment.LEFT, VAlignment.BOTTOM),
    DXFConstants.MTEXT_BOTTOM_CENTER: (HAlignment.CENTER, VAlignment.BOTTOM),
    DXFConstants.MTEXT_BOTTOM_RIGHT: (HAlignment.RIGHT, VAlignment.BOTTOM)
}
assert len(DXF_MTEXT_ALIGNMENT_TO_ALIGNMENT) == len(DXFConstants.MTEXT_ALIGN_FLAGS)


class FontMeasurements:
    def __init__(self, baseline: float, cap_height: float, x_height: float, descender_height: float):
        self.baseline = baseline
        self.cap_height = cap_height
        self.x_height = x_height
        self.descender_height = descender_height

    def __eq__(self, other):
        return (isinstance(other, FontMeasurements) and
                self.baseline == other.baseline and
                self.cap_height == other.cap_height and
                self.x_height == other.x_height and
                self.descender_height == other.descender_height)

    def scale_from_baseline(self, desired_cap_height: float) -> "FontMeasurements":
        scale = desired_cap_height / self.cap_height
        return FontMeasurements(
            baseline=self.baseline,
            cap_height=desired_cap_height,
            x_height=self.x_height * scale,
            descender_height=self.descender_height * scale,
        )

    @property
    def cap_top(self) -> float:
        return self.baseline + self.cap_height

    @property
    def x_top(self) -> float:
        return self.baseline + self.x_height

    @property
    def bottom(self) -> float:
        return self.baseline - self.descender_height


def _get_rotation(text: AnyText) -> Matrix44:
    if isinstance(text, Text):
        return Matrix44.axis_rotate(Vec3(text.dxf.extrusion).normalize(), radians(text.dxf.rotation))
    if isinstance(text, MText):
        return Matrix44.axis_rotate(Vec3(text.dxf.extrusion).normalize(), radians(text.get_rotation()))
    elif isinstance(text, Attrib):
        return Matrix44()
    else:
        raise TypeError(type(text))


def _get_alignment(text: AnyText) -> Alignment:
    if isinstance(text, Text):
        # for the purposes of rendering, the anchor is always the bottom left, text.get_align() should be ignored
        return HAlignment.LEFT, VAlignment.BASELINE
    elif isinstance(text, MText):
        return DXF_MTEXT_ALIGNMENT_TO_ALIGNMENT[text.dxf.attachment_point]
    elif isinstance(text, Attrib):
        return HAlignment.LEFT, VAlignment.BASELINE
    else:
        raise TypeError(type(text))


def _get_cap_height(text: AnyText) -> float:
    if isinstance(text, (Text, Attrib)):
        return text.dxf.height
    elif isinstance(text, MText):
        return text.dxf.char_height
    else:
        raise TypeError(type(text))


def _get_line_spacing(text: AnyText, cap_height: float) -> float:
    if isinstance(text, (Attrib, Text)):
        return 0.0
    elif isinstance(text, MText):
        return cap_height * DEFAULT_LINE_SPACING * text.dxf.line_spacing_factor
    else:
        raise TypeError(type(text))


def _split_multiline_text(text: str, box_width: Optional[float], get_text_width: Callable[[str], float]) -> List[str]:
    """
    This isn't the most straightforward word wrapping algorithm, but it aims to match the behavior of AutoCAD
    """
    if not text or text.isspace():
        return []
    manual_lines = re.split(r'(\n)', text)  # includes \n as it's own token
    tokens = [t for line in manual_lines for t in re.split(r'(\s+)', line) if t]
    lines = []
    current_line = ''
    line_just_wrapped = False

    for t in tokens:
        on_first_line = not lines
        if t == '\n' and line_just_wrapped:
            continue
        line_just_wrapped = False
        if t == '\n':
            lines.append(current_line.rstrip())
            current_line = ''
        elif t.isspace():
            if current_line or on_first_line:
                current_line += t
        else:
            if box_width is not None and get_text_width(current_line + t) > box_width:
                if not current_line:
                    current_line += t
                else:
                    lines.append(current_line.rstrip())
                    current_line = t
                    line_just_wrapped = True
            else:
                current_line += t

    if current_line and not current_line.isspace():
        lines.append(current_line.rstrip())
    return lines


def _split_into_lines(text: AnyText, box_width: Optional[float], get_text_width: Callable[[str], float]) -> List[str]:
    plain_text = text.plain_text()
    if isinstance(text, (Text, Attrib)):
        assert '\n' not in plain_text
        return [plain_text]
    else:
        return _split_multiline_text(plain_text, box_width, get_text_width)


def _get_text_width(text: AnyText) -> Optional[float]:
    if isinstance(text, (Attrib, Text)):
        return None
    elif isinstance(text, MText):
        width = text.dxf.width
        return None if width == 0.0 else width
    else:
        raise TypeError(type(text))


def _get_extra_transform(text: AnyText) -> Matrix44:
    extra_transform = Matrix44()
    if isinstance(text, Text):
        # ALIGNED: scaled to fit in the text box (aspect ratio preserved). Does not have to be handled specially.
        # FIT: scaled to fit in the text box (aspect ratio *not* preserved). Handled by dxf.width
        scale_x = text.dxf.width  # 'width' is the width *scale factor*
        scale_y = 1
        if text.dxf.text_generation_flag & DXFConstants.MIRROR_X:
            scale_x = -1
        if text.dxf.text_generation_flag & DXFConstants.MIRROR_Y:
            scale_y = -1

        # magnitude of extrusion does not have any effect. An extrusion of (0, 0, 0) acts like (0, 0, 1)
        scale_x *= sign(text.dxf.extrusion.z)

        if scale_x != 1 or scale_y != 1:
            extra_transform = Matrix44.scale(scale_x, scale_y)
    return extra_transform


def _apply_alignment(alignment: Alignment,
                     line_widths: List[float],
                     line_spacing: float,
                     box_width: Optional[float],
                     font_measurements: FontMeasurements) -> Tuple[Tuple[float, float], List[float], List[float]]:
    if not line_widths:
        return (0, 0), [], []

    halign, valign = alignment
    line_ys = [-font_measurements.baseline -
               (font_measurements.cap_height + i * line_spacing)
               for i in range(len(line_widths))]

    if box_width is None:
        box_width = max(line_widths)

    last_baseline = line_ys[-1]

    if halign == HAlignment.LEFT:
        anchor_x = 0
        line_xs = [0] * len(line_widths)
    elif halign == HAlignment.CENTER:
        anchor_x = box_width / 2
        line_xs = [anchor_x - w / 2 for w in line_widths]
    elif halign == HAlignment.RIGHT:
        anchor_x = box_width
        line_xs = [anchor_x - w for w in line_widths]
    else:
        raise ValueError(halign)

    if valign == VAlignment.TOP:
        anchor_y = 0
    elif valign == VAlignment.LOWER_CASE_CENTER:
        first_line_lower_case_top = line_ys[0] + font_measurements.x_height
        anchor_y = (first_line_lower_case_top + last_baseline) / 2
    elif valign == VAlignment.BASELINE:
        anchor_y = last_baseline
    elif valign == VAlignment.BOTTOM:
        anchor_y = last_baseline - font_measurements.descender_height
    else:
        raise ValueError(valign)

    return (anchor_x, anchor_y), line_xs, line_ys


def _get_wcs_insert(text: AnyText) -> Vec3:
    if isinstance(text, Text):
        return text.ocs().to_wcs(text.dxf.insert)
    else:
        return text.dxf.insert


def simplified_text_chunks(text: AnyText, out: Backend,
                           *,
                           font: fonts.Font = None,
                           debug_draw_rect: bool = False) -> Iterable[Tuple[str, Matrix44, float]]:
    """
    Splits a complex text entity into simple chunks of text which can all be rendered the same way:
    render the string (which will not contain any newlines) with the given cap_height with (left, baseline) at (0, 0)
    then transform it with the given matrix to move it into place.
    """
    alignment = _get_alignment(text)
    box_width = _get_text_width(text)

    cap_height = _get_cap_height(text)
    lines = _split_into_lines(text, box_width, lambda s: out.get_text_line_width(s, cap_height, font=font))
    line_spacing = _get_line_spacing(text, cap_height)
    line_widths = [out.get_text_line_width(line, cap_height, font=font) for line in lines]
    font_measurements = out.get_font_measurements(cap_height, font=font)
    anchor, line_xs, line_ys = \
        _apply_alignment(alignment, line_widths, line_spacing, box_width, font_measurements)
    rotation = _get_rotation(text)
    extra_transform = _get_extra_transform(text)
    insert = _get_wcs_insert(text)

    whole_text_transform = (
            Matrix44.translate(-anchor[0], -anchor[1], 0) @
            extra_transform @
            rotation @
            Matrix44.translate(*insert.xyz)
    )
    for i, (line, line_x, line_y) in enumerate(zip(lines, line_xs, line_ys)):
        transform = Matrix44.translate(line_x, line_y, 0) @ whole_text_transform
        yield line, transform, cap_height

        if debug_draw_rect:
            width = out.get_text_line_width(line, cap_height, font)
            ps = list(transform.transform_vertices([Vec3(0, 0, 0), Vec3(width, 0, 0), Vec3(width, cap_height, 0),
                                                    Vec3(0, cap_height, 0), Vec3(0, 0, 0)]))
            draw_rect(ps, '#ff0000', out)
