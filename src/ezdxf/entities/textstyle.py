# Created: 17.02.2019
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, RETURN_DEFAULT,
)
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['Textstyle']

acdb_style = DefSubclass('AcDbTextStyleTableRecord', {
    'name': DXFAttr(
        2, default='Standard',
        validator=validator.is_valid_table_name,
    ),
    'flags': DXFAttr(70, default=0),

    # Fixed height, 0 if not fixed
    'height': DXFAttr(
        40, default=0,
        validator=validator.is_greater_or_equal_zero,
        fixer=RETURN_DEFAULT,
    ),
    # Width factor:
    'width': DXFAttr(
        41, default=1,
        validator=validator.is_greater_zero,
        fixer=RETURN_DEFAULT,
    ),
    # Oblique angle in degree, 0 = vertical
    'oblique': DXFAttr(50, default=0),

    # Generation flags:
    # 2 = backward
    # 4 = mirrored in Y
    'generation_flags': DXFAttr(71, default=0),

    # Last height used:
    'last_height': DXFAttr(42, default=2.5),

    # Primary font file name:
    'font': DXFAttr(3, default='txt'),

    # Big font name, blank if none
    'bigfont': DXFAttr(4, default=''),
})


@register_entity
class Textstyle(DXFEntity):
    """ DXF STYLE entity """
    DXFTYPE = 'STYLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_style)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_style)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_style.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_style.name)

        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'flags', 'height', 'width', 'oblique', 'generation_flags',
            'last_height', 'font', 'bigfont'
        ])
