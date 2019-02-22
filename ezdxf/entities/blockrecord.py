# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2007, DXFInternalEzdxfError
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
    'layout': DXFAttr(340, default='0'),
    'explode': DXFAttr(280, default=1, dxfversion=DXF2007),  # 0 = can not explode; 1 = can explode
    'scale': DXFAttr(281, default=1, dxfversion=DXF2007),  # 0 = can not scale; 1 = can scale
    'units': DXFAttr(70, default=0, dxfversion=DXF2007),  # ezdxf.InsertUnits
    # 0 = Unitless
    # 1 = Inches
    # 2 = Feet
    # 3 = Miles
    # 4 = Millimeters
    # 5 = Centimeters
    # 6 = Meters
    # 7 = Kilometers
    # 8 = Microinches
    # 9 = Mils
    # 10 = Yards
    # 11 = Angstroms
    # 12 = Nanometers
    # 13 = Microns
    # 14 = Decimeters
    # 15 = Decameters
    # 16 = Hectometers
    # 17 = Gigameters
    # 18 = Astronomical units
    # 19 = Light years
    # 20 = Parsecs
    # 21 = US Survey Feet
    # 22 = US Survey Inch
    # 23 = US Survey Yard
    # 24 = US Survey Mile
    # ---------------------
    # 310: Binary data for bitmap preview (optional) - removed (ignored) by ezdxf
})

# optional XDATA for all DXF versions
# 1000: "ACAD"
# 1001: "DesignCenter Data" (optional)
# 1002: "{"
# 1070: Autodesk Design Center version number
# 1070: Insert units: like 'units'
# 1002: "}"


@register_entity
class BlockRecord(DXFEntity):
    """ DXF BLOCK_RECORD table entity """
    DXFTYPE = 'BLOCK_RECORD'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_blockrec)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_blockrec)
            if len(tags):  # not supported by DXF R12
                processor.log_unprocessed_tags(tags, subclass=acdb_blockrec.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion == DXF12:
            raise DXFInternalEzdxfError('Exporting BLOCK_RECORDS for DXF R12.')
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_blockrec.name)

        self.dxf.export_dxf_attribs(tagwriter, ['name', 'layout', 'units', 'explode', 'scale'])

