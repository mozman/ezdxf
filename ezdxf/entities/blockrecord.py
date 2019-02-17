# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXFStructureError
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.entities.dxfentity import DXFNamespace

__all__ = ['BlockRecord']


acdb_blockrec = DefSubclass('AcDbBlockTableRecord', {
    'name': DXFAttr(2),
    'layout': DXFAttr(340),
})


@register_entity
class BlockRecord(DXFEntity):
    """ DXF BLOCK_RECORD table entity """
    DXFTYPE = 'BLOCK_RECORD'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_blockrec)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_blockrec)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_blockrec.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion == DXF12:
            raise DXFStructureError('Exporting BLOCK_RECORDS for DXF R12.')
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_blockrec.name)

        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['name', 'layout'], force=True)

