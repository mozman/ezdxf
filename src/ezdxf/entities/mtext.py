# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import math
from typing import TYPE_CHECKING, Union, Tuple, List, Iterable

from ezdxf.lldxf import const, validator
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from ezdxf.lldxf.tags import Tags
from ezdxf.math import Vec3, Matrix44, OCS, NULLVEC, Z_AXIS, X_AXIS
from ezdxf.math.transformtools import transform_extrusion
from ezdxf.colors import rgb2int
from ezdxf.tools.text import (
    caret_decode, split_mtext_string, escape_dxf_line_endings, plain_mtext,
)
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import (
    TagWriter, DXFNamespace, DXFEntity, Vertex, Auditor, DXFTag,
)

__all__ = ['MText']

BG_FILL_MASK = 1 + 2 + 16

acdb_mtext = DefSubclass('AcDbMText', {
    'insert': DXFAttr(10, xtype=XType.point3d, default=NULLVEC),

    # Nominal (initial) text height
    'char_height': DXFAttr(
        40, default=2.5,
        validator=validator.is_greater_zero,
        fixer=RETURN_DEFAULT,
    ),

    # Reference column width
    'width': DXFAttr(41, optional=True),

    # Found in BricsCAD export:
    'defined_height': DXFAttr(46, dxfversion='AC1021'),

    # Attachment point:
    # 1 = Top left
    # 2 = Top center
    # 3 = Top right
    # 4 = Middle left
    # 5 = Middle center
    # 6 = Middle right
    # 7 = Bottom left
    # 8 = Bottom center
    # 9 = Bottom right
    'attachment_point': DXFAttr(
        71, default=1,
        validator=validator.is_in_integer_range(0, 10),
        fixer=RETURN_DEFAULT,
    ),

    # Flow direction:
    # 1 = Left to right
    # 3 = Top to bottom
    # 5 = By style (the flow direction is inherited from the associated
    #     text style)
    'flow_direction': DXFAttr(
        72, default=1, optional=True,
        validator=validator.is_one_of({1, 3, 5}),
        fixer=RETURN_DEFAULT,
    ),

    # Content text:
    # group code 1: text
    # group code 3: additional text (optional)

    # Text style name:
    'style': DXFAttr(
        7, default='Standard', optional=True,
        validator=validator.is_valid_table_name,  # do not fix!
    ),
    'extrusion': DXFAttr(
        210, xtype=XType.point3d, default=Z_AXIS, optional=True,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),

    # x-axis direction vector (in WCS)
    # If rotation and text_direction are present, text_direction wins
    'text_direction': DXFAttr(
        11, xtype=XType.point3d, default=X_AXIS, optional=True,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),

    # Horizontal width of the characters that make up the mtext entity.
    # This value will always be equal to or less than the value of *width*,
    # (read-only, ignored if supplied)
    'rect_width': DXFAttr(42, optional=True),

    # Vertical height of the mtext entity (read-only, ignored if supplied)
    'rect_height': DXFAttr(43, optional=True),

    # Text rotation in degrees -  Error in DXF reference, which claims radians
    'rotation': DXFAttr(50, default=0, optional=True),

    # Line spacing style (optional):
    # 1 = At least (taller characters will override)
    # 2 = Exact (taller characters will not override)
    'line_spacing_style': DXFAttr(
        73, default=1, optional=True,
        validator=validator.is_one_of({1, 2}),
        fixer=RETURN_DEFAULT,
    ),

    # Line spacing factor (optional): Percentage of default (3-on-5) line
    # spacing to be applied. Valid values range from 0.25 to 4.00
    'line_spacing_factor': DXFAttr(
        44, default=1, optional=True,
        validator=validator.is_in_float_range(0.25, 4.00),
        fixer=validator.fit_into_float_range(0.25, 4.00),
    ),

    # Determines how much border there is around the text.
    # (45) + (90) + (63) all three required, if one of them is used
    'box_fill_scale': DXFAttr(45, dxfversion='AC1021'),

    # background fill type flags:
    # 0 = off
    # 1 = color -> (63) < (421) or (431)
    # 2 = drawing window color
    # 3 = use background color (1 & 2)
    # 16 = text frame ODA specification 20.4.46
    'bg_fill': DXFAttr(
        90, dxfversion='AC1021',
        validator=validator.is_valid_bitmask(BG_FILL_MASK),
        fixer=validator.fix_bitmask(BG_FILL_MASK)
    ),

    # background fill color as ACI, required even true color is used
    'bg_fill_color': DXFAttr(
        63, dxfversion='AC1021',
        validator=validator.is_valid_aci_color,
    ),

    # 420-429? : background fill color as true color value, (63) also required
    # but ignored
    'bg_fill_true_color': DXFAttr(421, dxfversion='AC1021'),

    # 430-439? : background fill color as color name ???, (63) also required
    # but ignored
    'bg_fill_color_name': DXFAttr(431, dxfversion='AC1021'),

    # background fill color transparency - not used by AutoCAD/BricsCAD
    'bg_fill_transparency': DXFAttr(441, dxfversion='AC1021'),

})
acdb_mtext_group_codes = group_code_mapping(acdb_mtext)


# ----------------------------------------------------------------------
# NO MULTI-COLUMN SUPPORT
# ----------------------------------------------------------------------
# MTEXT column information will be preserved by ezdxf, but no further
# support for accessing the information nor to create multi-column MTEXT.
# The column definition is stored in XDATA 'ACAD' and new in DXF R2018
# as 'embedded object', but codes are different to codes in the
# DXF reference:
#
# code 75   Column type
# code 76	Column count
# code 78	Column Flow Reversed
# code 79	Column Auto height
# code 48	Column width
# code 49	Column gutter
#
# code 50	Column heights; this code is followed by a column count
# (Int16), and then the number of column heights
# ----------------------------------------------------------------------


@register_entity
class MText(DXFGraphic):
    """ DXF MTEXT entity """
    DXFTYPE = 'MTEXT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mtext)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    UNDERLINE_START = r'\L'
    UNDERLINE_STOP = r'\l'
    UNDERLINE = UNDERLINE_START + '%s' + UNDERLINE_STOP
    OVERSTRIKE_START = r'\O'
    OVERSTRIKE_STOP = r'\o'
    OVERSTRIKE = OVERSTRIKE_START + '%s' + OVERSTRIKE_STOP
    STRIKE_START = r'\K'
    STRIKE_STOP = r'\k'
    STRIKE = STRIKE_START + '%s' + STRIKE_STOP
    NEW_LINE = r'\P'
    GROUP_START = '{'
    GROUP_END = '}'
    GROUP = GROUP_START + '%s' + GROUP_END
    NBSP = r'\~'  # non breaking space

    def __init__(self):
        """ Default constructor """
        super().__init__()
        self.text: str = ""

    def _copy_data(self, entity: 'DXFEntity') -> None:
        """ Copy entity data: text """
        entity.text = self.text

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = Tags(self.load_mtext(processor.subclass_by_index(2)))
            processor.fast_load_dxfattribs(
                dxf, acdb_mtext_group_codes, subclass=tags, recover=True)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_mtext.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'char_height', 'width', 'defined_height',
            'attachment_point', 'flow_direction',
        ])
        self.export_mtext(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, [
            'style', 'extrusion', 'text_direction', 'rect_width', 'rect_height',
            'rotation', 'line_spacing_style', 'line_spacing_factor',
            'box_fill_scale', 'bg_fill', 'bg_fill_color', 'bg_fill_true_color',
            'bg_fill_color_name', 'bg_fill_transparency',
        ])

    def load_mtext(self, tags: Tags) -> Iterable['DXFTag']:
        tail = ""
        parts = []
        for tag in tags:
            if tag.code == 1:
                tail = tag.value
            elif tag.code == 3:
                parts.append(tag.value)
            else:
                yield tag
        parts.append(tail)
        self.text = escape_dxf_line_endings(caret_decode("".join(parts)))

    def export_mtext(self, tagwriter: 'TagWriter') -> None:
        txt = escape_dxf_line_endings(self.text)
        str_chunks = split_mtext_string(txt, size=250)
        if len(str_chunks) == 0:
            str_chunks.append("")
        while len(str_chunks) > 1:
            tagwriter.write_tag2(3, str_chunks.pop(0))
        tagwriter.write_tag2(1, str_chunks[0])

    def get_rotation(self) -> float:
        """ Get text rotation in degrees, independent if it is defined by
        :attr:`dxf.rotation` or :attr:`dxf.text_direction`.

        """
        if self.dxf.hasattr('text_direction'):
            vector = self.dxf.text_direction
            radians = math.atan2(vector[1], vector[0])  # ignores z-axis
            rotation = math.degrees(radians)
        else:
            rotation = self.dxf.get('rotation', 0)
        return rotation

    def set_rotation(self, angle: float) -> 'MText':
        """ Set attribute :attr:`rotation` to `angle` (in degrees) and deletes
        :attr:`dxf.text_direction` if present.

        """
        # text_direction has higher priority than rotation, therefore delete it
        self.dxf.discard('text_direction')
        self.dxf.rotation = angle
        return self  # fluent interface

    def set_location(self, insert: 'Vertex', rotation: float = None,
                     attachment_point: int = None) -> 'MText':
        """ Set attributes :attr:`dxf.insert`, :attr:`dxf.rotation` and
        :attr:`dxf.attachment_point`, ``None`` for :attr:`dxf.rotation` or
        :attr:`dxf.attachment_point` preserves the existing value.

        """
        self.dxf.insert = Vec3(insert)
        if rotation is not None:
            self.set_rotation(rotation)
        if attachment_point is not None:
            self.dxf.attachment_point = attachment_point
        return self  # fluent interface

    def set_bg_color(self, color: Union[int, str, Tuple[int, int, int], None],
                     scale: float = 1.5):
        """ Set background color as :ref:`ACI` value or as name string or as RGB
        tuple ``(r, g, b)``.

        Use special color name ``canvas``, to set background color to canvas
        background color.

        Args:
            color: color as :ref:`ACI`, string or RGB tuple
            scale: determines how much border there is around the text, the
                value is based on the text height, and should be in the range
                of [1, 5], where 1 fits exact the MText entity.

        """
        if 1 <= scale <= 5:
            self.dxf.box_fill_scale = scale
        else:
            raise ValueError('argument scale has to be in range from 1 to 5.')
        if color is None:
            self.dxf.discard('bg_fill')
            self.dxf.discard('box_fill_scale')
            self.dxf.discard('bg_fill_color')
            self.dxf.discard('bg_fill_true_color')
            self.dxf.discard('bg_fill_color_name')
        elif color == 'canvas':  # special case for use background color
            self.dxf.bg_fill = const.MTEXT_BG_CANVAS_COLOR
            self.dxf.bg_fill_color = 0  # required but ignored
        else:
            self.dxf.bg_fill = const.MTEXT_BG_COLOR
            if isinstance(color, int):
                self.dxf.bg_fill_color = color
            elif isinstance(color, str):
                self.dxf.bg_fill_color = 0  # required but ignored
                self.dxf.bg_fill_color_name = color
            elif isinstance(color, tuple):
                self.dxf.bg_fill_color = 0  # required but ignored
                self.dxf.bg_fill_true_color = rgb2int(color)
        return self  # fluent interface

    def __iadd__(self, text: str) -> 'MText':
        """ Append `text` to existing content (:attr:`.text` attribute). """
        self.text += text
        return self

    append = __iadd__

    def set_font(self, name: str, bold: bool = False, italic: bool = False,
                 codepage: int = 1252, pitch: int = 0) -> None:
        """ Append font change (e.g. ``'\\Fkroeger|b0|i0|c238|p10'`` ) to
        existing content (:attr:`.text` attribute).

        Args:
            name: font name
            bold: flag
            italic: flag
            codepage: character codepage
            pitch: font size

        """
        s = rf"\F{name}|b{int(bold)}|i{int(italic)}|c{codepage}|p{pitch};"
        self.append(s)

    def set_color(self, color_name: str) -> None:
        """ Append text color change to existing content, `color_name` as
        ``red``, ``yellow``, ``green``, ``cyan``, ``blue``, ``magenta`` or
        ``white``.

        """
        self.append(r"\C%d" % const.MTEXT_COLOR_INDEX[color_name.lower()])

    def add_stacked_text(self, upr: str, lwr: str, t: str = '^') -> None:
        r"""
        Add stacked text `upr` over `lwr`, `t` defines the kind of stacking:

        .. code-block:: none

            "^": vertical stacked without divider line, e.g. \SA^B:
                 A
                 B

            "/": vertical stacked with divider line,  e.g. \SX/Y:
                 X
                 -
                 Y

            "#": diagonal stacked, with slanting divider line, e.g. \S1#4:
                 1/4

        """
        # space ' ' in front of {lwr} is important
        self.append(r'\S{upr}{t} {lwr};'.format(upr=upr, lwr=lwr, t=t))

    def transform(self, m: Matrix44) -> 'MText':
        """ Transform MTEXT entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        old_extrusion = Vec3(dxf.extrusion)
        new_extrusion, _ = transform_extrusion(old_extrusion, m)

        if dxf.hasattr('rotation') and not dxf.hasattr('text_direction'):
            # MTEXT is not an OCS entity, but I don't know how else to convert
            # a rotation angle for an entity just defined by an extrusion vector.
            # It's correct for the most common case: extrusion=(0, 0, 1)
            ocs = OCS(old_extrusion)
            dxf.text_direction = ocs.to_wcs(Vec3.from_deg_angle(dxf.rotation))

        dxf.discard('rotation')

        old_text_direction = Vec3(dxf.text_direction)
        new_text_direction = m.transform_direction(old_text_direction)

        old_char_height_vec = old_extrusion.cross(old_text_direction).normalize(
            dxf.char_height)
        new_char_height_vec = m.transform_direction(old_char_height_vec)
        oblique = new_text_direction.angle_between(new_char_height_vec)
        dxf.char_height = new_char_height_vec.magnitude * math.sin(oblique)

        if dxf.hasattr('width'):
            width_vec = old_text_direction.normalize(dxf.width)
            dxf.width = m.transform_direction(width_vec).magnitude

        dxf.insert = m.transform(dxf.insert)
        dxf.text_direction = new_text_direction
        dxf.extrusion = new_extrusion
        return self

    def plain_text(self, split=False) -> Union[List[str], str]:
        """ Returns text content without formatting codes.

        Args:
            split: returns list of strings splitted at line breaks if ``True``
                else returns a single string.

        """
        return plain_mtext(self.text, split=split)

    def audit(self, auditor: 'Auditor'):
        """ Validity check. """
        super().audit(auditor)
        auditor.check_text_style(self)
