# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-16
from typing import TYPE_CHECKING, Iterable
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from .dxfentity import DXFNamespace, DXFEntity
    from ezdxf.drawing2 import Drawing

__all__ = ['Insert']

acdb_block_reference = DefSubclass('AcDbBlockReference', {
    'attribs_follow': DXFAttr(66, default=0),
    'name': DXFAttr(2),
    'insert': DXFAttr(10, xtype=XType.any_point),
    'xscale': DXFAttr(41, default=1.0),
    'yscale': DXFAttr(42, default=1.0),
    'zscale': DXFAttr(43, default=1.0),
    'rotation': DXFAttr(50, default=0.0),
    'column_count': DXFAttr(70, default=1),
    'row_count': DXFAttr(71, default=1),
    'column_spacing': DXFAttr(44, default=0.0),
    'row_spacing': DXFAttr(45, default=0.0),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0.0, 0.0, 1.0)),
})


@register_entity
class Insert(DXFGraphic):
    """ DXF INSERT entity """
    DXFTYPE = 'INSERT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_block_reference)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.attribs = []

    def linked_entities(self) -> Iterable['DXFEntity']:
        return self.attribs

    def link_entity(self, entity: 'DXFEntity') -> None:
        self.attribs.append(entity)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class and 'AcDbEntity' processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_block_reference)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_block_reference.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_block_reference.name)
        # for all DXF versions
        if len(self.attribs):
            self.dxf.export_dxf_attribute(tagwriter, 'attribs_follow')
        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'insert',
            'xscale', 'yscale', 'zscale',
            'rotation',
            'column_count', 'row_count',
            'column_spacing', 'row_spacing',
            'extrusion',
        ])

        # xdata and embedded objects export will be done by parent class
        # following SEQEND is exported by EntitySpace()

    def destroy(self) -> None:
        """
        Delete all data and references.

        """
        for a in self.attribs:
            a.destroy()
        del self.attribs
        super().destroy()
