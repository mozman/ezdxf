# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2000, DXF2007, DXFInvalidLayerName
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.lldxf.validator import is_valid_layer_name

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.entities.dxfentity import DXFNamespace

__all__ = ['Layer']

acdb_symbol_table_record = DefSubclass('AcDbSymbolTableRecord', {})

acdb_layer_table_record = DefSubclass('AcDbLayerTableRecord', {
    'name': DXFAttr(2),  # layer name
    'flags': DXFAttr(70, default=0),
    'color': DXFAttr(62, default=7),  # dxf color index
    'linetype': DXFAttr(6, default='Continuous'),  # linetype name
    'plot': DXFAttr(290, default=1, dxfversion=DXF2000),  # don't plot this layer if 0 else 1
    'lineweight': DXFAttr(370, default=-3, dxfversion=DXF2000),  # 1/100 mm, min 13 = 0.13mm, max 200 = 2.0mm

    # code 390 is required for AutoCAD
    # Pointer/handle to PlotStyleName
    # uses tag(390, ...) from the '0' layer1
    'plot_style_name': DXFAttr(390, dxfversion=DXF2000),  # handle to PlotStyleName object
    'material': DXFAttr(347, dxfversion=DXF2007),  # handle to Material object
})


class Layer(DXFEntity):
    """ DXF LINE entity """
    DXFTYPE = 'LINE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_layer_table_record)
    FROZEN = 0b00000001
    THAW = 0b11111110
    LOCK = 0b00000100
    UNLOCK = 0b11111011

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class and 'AcDbEntity' processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_layer_table_record)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_layer_table_record.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_layer_table_record.name)

        # for all DXF versions
        self.dxf.export_dxf_attribute(tagwriter, 'name', force=True)
        self.dxf.export_dxf_attribute(tagwriter, 'flags', force=True)
        self.dxf.export_dxf_attribute(tagwriter, 'color', force=True)
        self.dxf.export_dxf_attribute(tagwriter, 'linetype', force=True)

        if tagwriter.dxfversion >= DXF2000:
            self.dxf.export_dxf_attribute(tagwriter, 'plot')  # no force required
            self.dxf.export_dxf_attribute(tagwriter, 'lineweight', force=True)
            self.dxf.export_dxf_attribute(tagwriter, 'plot_style_name')  # required and always set

        if tagwriter.dxfversion >= DXF2007:
            self.dxf.export_dxf_attribute(tagwriter, 'material')  # required and always set

    def post_new_hook(self) -> None:
        if not is_valid_layer_name(self.dxf.name):
            raise DXFInvalidLayerName("Invalid layer name '{}'".format(self.dxf.name))

    def is_frozen(self) -> bool:
        return self.dxf.flags & Layer.FROZEN > 0

    def freeze(self) -> None:
        self.dxf.flags = self.dxf.flags | Layer.FROZEN

    def thaw(self) -> None:
        self.dxf.flags = self.dxf.flags & Layer.THAW

    def is_locked(self) -> bool:
        return self.dxf.flags & Layer.LOCK > 0

    def lock(self) -> None:
        self.dxf.flags = self.dxf.flags | Layer.LOCK

    def unlock(self) -> None:
        self.dxf.flags = self.dxf.flags & Layer.UNLOCK

    def is_off(self) -> bool:
        return self.dxf.color < 0

    def is_on(self) -> bool:
        return not self.is_off()

    def on(self) -> None:
        self.dxf.color = abs(self.dxf.color)

    def off(self) -> None:
        self.dxf.color = -abs(self.dxf.color)

    def get_color(self) -> int:
        return abs(self.dxf.color)

    def set_color(self, color: int) -> None:
        color = abs(color) if self.is_on() else -abs(color)
        self.dxf.color = color
