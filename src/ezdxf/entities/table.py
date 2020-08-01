# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import (
    DXF2000, STRUCTURE_MARKER, OWNER_CODE, SUBCLASS_MARKER,
    DXFInternalEzdxfError,
)

from .dxfentity import SubclassProcessor, DXFEntity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['TableHead']

base_class = DefSubclass(None, {
    'name': DXFAttr(2),
    'handle': DXFAttr(5),
    'owner': DXFAttr(330),
})

acdb_symbol_table = DefSubclass('AcDbSymbolTable', {
    'count': DXFAttr(70, default=0),
})


@register_entity
class TableHead(DXFEntity):
    DXFTYPE = 'TABLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table)

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            dxf.name = processor.base_class.get_first_value(2)
            dxf.count = 0  # no need to load max table count
        return dxf

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        if self.dxf.handle is None:
            raise DXFInternalEzdxfError(
                'TABLE needs a handle, maybe loaded from DXF R12 without handle!')
        # 1. tag: (0, DXFTYPE)
        tagwriter.write_tag2(STRUCTURE_MARKER, self.DXFTYPE)
        tagwriter.write_tag2(2, self.dxf.name)
        if tagwriter.dxfversion >= DXF2000:
            tagwriter.write_tag2(5, self.dxf.handle)
            if self.extension_dict:
                self.extension_dict.export_dxf(tagwriter)
            tagwriter.write_tag2(OWNER_CODE, self.dxf.owner)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table.name)
            tagwriter.write_tag2(70, self.dxf.count)
            if self.dxf.name == 'DIMSTYLE':  # the one exception - typical Autodesk
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbDimStyleTable')
        else:  # DXF R12
            #  TABLE does not need a handle at all
            tagwriter.write_tag2(70, self.dxf.count)
