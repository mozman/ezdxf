# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import logging
from ezdxf.lldxf import validator, const
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from .factory import register_entity

logger = logging.getLogger("ezdxf")

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ["Textstyle"]

acdb_style = DefSubclass(
    "AcDbTextStyleTableRecord",
    {
        "name": DXFAttr(
            2,
            default="Standard",
            validator=validator.is_valid_table_name,
        ),
        # Flags: Standard flag values (bit-coded values):
        # 1 = If set, this entry describes a shape
        # 4 = Vertical text
        # 16 = If set, table entry is externally dependent on an xref
        # 32 = If both this bit and bit 16 are set, the externally dependent xref ...
        # 64 = If set, the table entry was referenced by at least one entity in ...
        # Vertical text works only for SHX fonts in AutoCAD and BricsCAD
        "flags": DXFAttr(70, default=0),
        # Fixed height, 0 if not fixed
        "height": DXFAttr(
            40,
            default=0,
            validator=validator.is_greater_or_equal_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Width factor:  a.k.a. "Stretch"
        "width": DXFAttr(
            41,
            default=1,
            validator=validator.is_greater_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Oblique angle in degree, 0 = vertical
        "oblique": DXFAttr(50, default=0),
        # Generation flags:
        # 2 = backward
        # 4 = mirrored in Y
        "generation_flags": DXFAttr(71, default=0),
        # Last height used:
        "last_height": DXFAttr(42, default=2.5),
        # Primary font file name:
        # ATTENTION: The font file name can be an empty string and the font family
        # may be stored in XDATA! See also posts at the (unrelated) issue #380.
        "font": DXFAttr(3, default="txt"),
        # Big font name, blank if none
        "bigfont": DXFAttr(4, default=""),
    },
)
acdb_style_group_codes = group_code_mapping(acdb_style)


# XDATA: This is not a reliable source for font data!
# 1001 <ctrl> ACAD
# 1000 <str> Arial  ; font-family sometimes an empty string!
# 1071 <int> 34  ; flags
# ----
# "Arial" "normal" flags = 34               = 0b00:00000000:00000000:00100010
# "Arial" "italic" flags = 16777250         = 0b01:00000000:00000000:00100010
# "Arial" "bold" flags = 33554466           = 0b10:00000000:00000000:00100010
# "Arial" "bold+italic" flags = 50331682    = 0b11:00000000:00000000:00100010


@register_entity
class Textstyle(DXFEntity):
    """DXF STYLE entity"""

    DXFTYPE = "STYLE"
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_style)
    BOLD = 0b01000000000000000000000000
    ITALIC = 0b10000000000000000000000000

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(dxf, acdb_style_group_codes, 2)
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        super().export_entity(tagwriter)
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_style.name)

        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "name",
                "flags",
                "height",
                "width",
                "oblique",
                "generation_flags",
                "last_height",
                "font",
                "bigfont",
            ],
        )

    @property
    def has_extended_font_data(self) -> bool:
        """Returns ``True`` if extended font data is present."""
        return self.has_xdata("ACAD")

    def get_extended_font_data(self) -> Tuple[str, bool, bool]:
        """Returns extended font data as tuple (font-family, italic-flag,
        bold-flag).

        The extended font data is optional and not reliable! Returns
        ("", ``False``, ``False``) if extended font data is not present.

        """
        family = ""
        italic = False
        bold = False
        try:
            xdata = self.get_xdata("ACAD")
        except const.DXFValueError:
            pass
        else:
            if len(xdata) > 1:
                group_code, value = xdata[0]
                if group_code == 1000:
                    family = value
                group_code, value = xdata[1]
                if group_code == 1071:
                    italic = bool(self.ITALIC & value)
                    bold = bool(self.BOLD & value)
        return family, italic, bold

    def set_extended_font_data(
        self, family: str = "", *, italic=False, bold=False
    ) -> None:
        """Set extended font data, the font-family name `family` is not
        validated by `ezdxf`. Overwrites existing data.
        """
        if self.has_xdata("ACAD"):
            self.discard_xdata("ACAD")

        flags = 34  # unknown default flags
        if italic:
            flags += self.ITALIC
        if bold:
            flags += self.BOLD
        self.set_xdata("ACAD", [(1000, family), (1071, flags)])

    def discard_extended_font_data(self):
        """Discard extended font data."""
        self.discard_xdata("ACAD")

    @property
    def is_backward(self) -> bool:
        """Get/set text generation flag BACKWARDS, for mirrored text along the
        x-axis.
        """
        return self.get_flag_state(const.BACKWARD, "generation_flags")

    @is_backward.setter
    def is_backward(self, state) -> None:
        self.set_flag_state(const.BACKWARD, state, "generation_flags")

    @property
    def is_upside_down(self) -> bool:
        """Get/set text generation flag UPSIDE_DOWN, for mirrored text along
        the y-axis.

        """
        return self.get_flag_state(const.UPSIDE_DOWN, "generation_flags")

    @is_upside_down.setter
    def is_upside_down(self, state) -> None:
        self.set_flag_state(const.UPSIDE_DOWN, state, "generation_flags")

    @property
    def is_vertical_stacked(self) -> bool:
        """Get/set style flag VERTICAL_STACKED, for vertical stacked text."""
        return self.get_flag_state(const.VERTICAL_STACKED, "flags")

    @is_vertical_stacked.setter
    def is_vertical_stacked(self, state) -> None:
        self.set_flag_state(const.VERTICAL_STACKED, state, "flags")
