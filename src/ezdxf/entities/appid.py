# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, group_code_mapping,
)
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from ezdxf.lldxf.validator import is_valid_table_name
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['AppID']

acdb_appid = DefSubclass('AcDbRegAppTableRecord', {
    'name': DXFAttr(2, validator=is_valid_table_name),
    'flags': DXFAttr(70, default=0),
})

acdb_appid_group_codes = group_code_mapping(acdb_appid)


@register_entity
class AppID(DXFEntity):
    """ DXF APPID entity """
    DXFTYPE = 'APPID'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_appid)

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_appid_group_codes, subclass=2)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_appid.name)

        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['name', 'flags'])
