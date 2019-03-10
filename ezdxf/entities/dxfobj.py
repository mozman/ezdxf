# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFObject - non graphical entities stored in OBJECTS section
from typing import TYPE_CHECKING, Iterable
from ezdxf.lldxf.const import DXF2000, DXFStructureError, SUBCLASS_MARKER
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import dxftag, DXFTag
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from .dxfentity import DXFEntity, base_class, SubclassProcessor
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import Auditor, Drawing, DXFNamespace, TagWriter

__all__ = ['DXFObject', 'AcDbPlaceholder']


class DXFObject(DXFEntity):
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000


@register_entity
class AcDbPlaceholder(DXFObject):
    DXFTYPE = 'ACDBPLACEHOLDER'


acdb_xrecord = DefSubclass('AcDbXrecord', {
    'cloning': DXFAttr(280, default=1),
    # 0=not applicable; 1=keep existing; 2=use clone; 3=<xref>$0$<name>; 4=$0$<name>; 5=Unmangle name
})


def totags(tags: Iterable)->Iterable[DXFTag]:
    for tag in tags:
        if isinstance(tag, DXFTag):
            yield tag
        else:
            yield dxftag(tag[0], tag[1])


@register_entity
class XRecord(DXFObject):
    DXFTYPE = 'XRECORD'
    DXFATTRIBS = DXFAttributes(base_class, acdb_xrecord)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.tags = Tags()

    def _copy_data(self, entity: 'XRecord') -> None:
        """ Copy tag. """
        entity.tags = Tags(entity.tags)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for AcDbPolyline, requires previous base class and AcDbEntity processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.subclasses[1]
            if tags:
                if len(tags) < 2:
                    raise DXFStructureError('Invalid AcDbXrecord')
                code, value = tags[1]
                if code == 280:
                    dxf.cloning = value
                else:
                    raise DXFStructureError('Expected group code 280 as first tag in AcDbXrecord')
                self.tags = Tags(tags[2:])
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_xrecord.name)
        tagwriter.write_tag2(280, self.dxf.cloning)
        tagwriter.write_tags(Tags(totags(self.tags)))
