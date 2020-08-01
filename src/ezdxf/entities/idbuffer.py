# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT-License
# Created: 2019-03-11
from typing import TYPE_CHECKING, List
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXFStructureError
from ezdxf.lldxf.attributes import DXFAttributes, DefSubclass, DXFAttr
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace, Tags

__all__ = ['IDBuffer', 'FieldList', 'LayerFilter']

acdb_id_buffer = DefSubclass('AcDbIdBuffer', {})


@register_entity
class IDBuffer(DXFObject):
    """ DXF IDBUFFER entity """
    DXFTYPE = 'IDBUFFER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_id_buffer)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.handles = []  # type: List[str]

    def _copy_data(self, entity: 'IDBuffer') -> None:
        """ Copy handles """
        entity.handles = list(self.handles)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            if len(processor.subclasses) < 2:
                raise DXFStructureError(
                    f'Missing required subclass in IDBUFFER(#{dxf.handle})')
            self.load_handles(processor.subclasses[1])
        return dxf

    def load_handles(self, tags: 'Tags'):
        self.handles = [value for code, value in tags if code == 330]

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_id_buffer.name)
        self.export_handles(tagwriter)

    def export_handles(self, tagwriter: 'TagWriter'):
        for handle in self.handles:
            tagwriter.write_tag2(330, handle)


acdb_id_set = DefSubclass('AcDbIdSet', {
    'flags': DXFAttr(90, default=0),  # not documented by Autodesk
})
acdb_field_list = DefSubclass('AcDbFieldList', {})


@register_entity
class FieldList(IDBuffer):
    """ DXF FIELDLIST entity """
    DXFTYPE = 'FIELDLIST'
    DXFATTRIBS = DXFAttributes(base_class, acdb_id_set, acdb_field_list)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super(DXFObject, self).load_dxf_attribs(processor)
        if processor:
            if len(processor.subclasses) < 3:
                raise DXFStructureError(
                    f'Missing required subclass in FIELDLIST(#{dxf.handle})')
            processor.load_dxfattribs_into_namespace(dxf, acdb_id_set)
            self.load_handles(processor.subclasses[2])
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super(DXFObject, self).export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_id_set.name)
        self.dxf.export_dxf_attribs(tagwriter, 'flags')
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_field_list.name)
        self.export_handles(tagwriter)


acdb_filter = DefSubclass('AcDbFilter', {})
acdb_layer_filter = DefSubclass('AcDbLayerFilter', {})


@register_entity
class LayerFilter(IDBuffer):
    """ DXF LAYER_FILTER entity """
    DXFTYPE = 'LAYER_FILTER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_filter, acdb_layer_filter)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super(DXFObject, self).load_dxf_attribs(processor)
        if processor:
            if len(processor.subclasses) < 3:
                raise DXFStructureError(
                    f'Missing required subclass in LAYER_FILTER(#{dxf.handle})')
            self.load_handles(processor.subclasses[2])
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super(DXFObject, self).export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_filter.name)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_layer_filter.name)
        self.export_handles(tagwriter)
