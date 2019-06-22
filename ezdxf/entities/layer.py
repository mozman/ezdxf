# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2000, DXF2007, DXF2004, DXFInvalidLayerName
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.lldxf.validator import is_valid_layer_name
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['Layer']

acdb_symbol_table_record = DefSubclass('AcDbSymbolTableRecord', {})

acdb_layer_table_record = DefSubclass('AcDbLayerTableRecord', {
    'name': DXFAttr(2),  # layer name
    'flags': DXFAttr(70, default=0),
    'color': DXFAttr(62, default=7),  # dxf color index
    'true_color': DXFAttr(420, dxfversion=DXF2004, optional=True),  # true color
    'linetype': DXFAttr(6, default='Continuous'),  # linetype name
    'plot': DXFAttr(290, default=1, dxfversion=DXF2000, optional=True),  # don't plot this layer if 0 else 1
    'lineweight': DXFAttr(370, default=-3, dxfversion=DXF2000),  # 1/100 mm, min 13 = 0.13mm, max 200 = 2.0mm

    # code 390 is required for AutoCAD
    # Pointer/handle to PlotStyleName
    # uses tag(390, ...) from the '0' layer1
    'plotstyle_handle': DXFAttr(390, dxfversion=DXF2000),  # handle to PlotStyleName object
    'material_handle': DXFAttr(347, dxfversion=DXF2007),  # handle to Material object
    'unknown1': DXFAttr(348, dxfversion=DXF2007, optional=True),  # handle to ???

})


@register_entity
class Layer(DXFEntity):
    """ DXF LAYER entity """
    DXFTYPE = 'LAYER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_layer_table_record)
    DEFAULT_ATTRIBS = {'name': '0'}
    FROZEN = 0b00000001
    THAW = 0b11111110
    LOCK = 0b00000100
    UNLOCK = 0b11111011

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_layer_table_record)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_layer_table_record.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_layer_table_record.name)

        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'flags', 'color', 'true_color', 'linetype', 'plot', 'lineweight', 'plotstyle_handle',
            'material_handle', 'unknown1',
        ])

    def post_new_hook(self) -> None:
        if not is_valid_layer_name(self.dxf.name):
            raise DXFInvalidLayerName("Invalid layer name '{}'".format(self.dxf.name))

    def set_required_attributes(self):
        if not self.dxf.hasattr('material'):
            self.dxf.material_handle = self.doc.materials['Global'].dxf.handle
        if not self.dxf.hasattr('plotstyle_handle'):
            self.dxf.plotstyle_handle = self.doc.plotstyles['Normal'].dxf.handle

    def is_frozen(self) -> bool:
        """ Returns ``True`` if layer is frozen. """
        return self.dxf.flags & Layer.FROZEN > 0

    def freeze(self) -> None:
        """ Freeze layer. """
        self.dxf.flags = self.dxf.flags | Layer.FROZEN

    def thaw(self) -> None:
        """ Thaw layer."""
        self.dxf.flags = self.dxf.flags & Layer.THAW

    def is_locked(self) -> bool:
        """ Returns ``True`` if layer is locked. """
        return self.dxf.flags & Layer.LOCK > 0

    def lock(self) -> None:
        """ Lock layer, entities on this layer are not editable - just important in CAD applications. """
        self.dxf.flags = self.dxf.flags | Layer.LOCK

    def unlock(self) -> None:
        """ Unlock layer, entities on this layer are editable - just important in CAD applications. """
        self.dxf.flags = self.dxf.flags & Layer.UNLOCK

    def is_off(self) -> bool:
        """ Returns ``True`` if layer is off. """
        return self.dxf.color < 0

    def is_on(self) -> bool:
        """ Returns ``True`` if layer is on. """
        return not self.is_off()

    def on(self) -> None:
        """ Switch layer `on` (visible)."""
        self.dxf.color = abs(self.dxf.color)

    def off(self) -> None:
        """ Switch layer `off` (invisible). """
        self.dxf.color = -abs(self.dxf.color)

    def get_color(self) -> int:
        """ Get layer color, preferred method for getting the layer color, because color is negative for layer
        status `off`.
        """
        return abs(self.dxf.color)

    def set_color(self, color: int) -> None:
        """ Set layer `color`, preferred method for setting the layer color, because color is negative for layer
        status `off`.
        """
        color = abs(color) if self.is_on() else -abs(color)
        self.dxf.color = color
