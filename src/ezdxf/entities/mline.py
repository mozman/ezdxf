# Created: 08.04.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List
from collections import OrderedDict, namedtuple

from ezdxf.lldxf.const import SUBCLASS_MARKER, DXFTypeError
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic, acdb_entity
from .objectcollection import ObjectCollection
from ezdxf.entities.factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace

__all__ = ['MLine', 'MLineStyle', 'MLineStyleCollection']

# example: processing: D:\source\dxftest\CADKitSamples\Lock-Off.dxf


acdb_mline = DefSubclass('AcDbMline', OrderedDict({
    'mline_style': DXFAttr(2, default='Standard'),  # name of MLineStyle
    'mline_style_id': DXFAttr(340, default=0),  # handle of MLineStyle
    'scale_factor': DXFAttr(40, default=1),
    'justification': DXFAttr(70, default=0),  # 0 = Top; 1 = Zero; 2 = Bottom
    'flags': DXFAttr(71, default=1),  # Flags (bit-coded values):
    # 1 = Has at least one vertex (code 72 is greater than 0)
    # 2 = Closed
    # 4 = Suppress start caps
    # 8 = Suppress end caps
    'n_vertices': DXFAttr(72, default=0),  # Number of vertices
    'n_style_elements': DXFAttr(73, default=1),  # Number of elements in MLINESTYLE definition
    'start_point': DXFAttr(10, xtype=XType.point3d, default=(0, 0, 0)),  # in WCS!
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0, 0, 1)),  # but all vertices in WCS!
    # 11: vertex coordinates (multiple entries; one entry for each vertex)
    # 12: Direction vector of segment starting at this vertex (multiple entries; one for each vertex)
    # 13: Direction vector of miter at this vertex (multiple entries: one for each vertex)
    # 73: Number of parameters for this element (repeats for each element in segment)
    # 41: Element parameters (repeats based on previous code 74)
    # 75: Number of area fill parameters for this element (repeats for each element in segment)
    # 42: Area fill parameters (repeats based on previous code 75)
}))


# The group code 41 parameterization is a list of real values, one real per group code 41. The list may contain zero or
# more items. The first group code 41 value is the distance from the segment vertex along the miter vector to the point
# where the line element's path intersects the miter vector. The next group code 41 value is the distance along the line
# element's path from the point defined by the first group 41 to the actual start of the line element. The next is the
# distance from the start of the line element to the first break (or cut) in the line element. The successive group
# code 41 values continue to list the start and stop points of the line element in this segment of the mline. Linetypes
# do not affect group 41 lists.
#
# The group code 42 parameterization is also a list of real values. Similar to the 41 parameterization, it describes the
# parameterization of the fill area for this mline segment. The values are interpreted identically to the 41 parameters
# and when taken as a whole for all line elements in the mline segment, they define the boundary of the fill area for
# the mline segment.
#
# A common example of the use of the group code 42 mechanism is when an unfilled mline crosses over a filled mline and
# mledit is used to cause the filled mline to appear unfilled in the crossing area. This would result in two group 42s
# for each line element in the affected mline segment; one for the fill stop and one for the fill start.
#
# The 2 group codes in mline entities and mlinestyle objects are redundant fields. These groups should not be modified
# under any circumstances, although it is safe to read them and use their values. The correct fields to modify are as
# follows:
#
# Mline
# The 340 group in the same object, which indicates the proper MLINESTYLE object.
#
# Mlinestyle
# The 3 group value in the MLINESTYLE dictionary, which precedes the 350 group that has the handle or entity name of
# the current mlinestyle.

class MLineVertices:
    """ For now just store tags """

    def __init__(self, tags):
        self.tags = tags

    def __len__(self):
        return len(self.tags)

    def export_dxf(self, tagwriter: 'TagWriter'):
        tagwriter.write_tags(self.tags)


@register_entity
class MLine(DXFGraphic):
    DXFTYPE = 'MLINE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mline)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        # todo: MLINE implementation
        self.vertices = MLineVertices([])

    def copy(self):
        raise DXFTypeError('Cloning of {} not supported.'.format(self.DXFTYPE))

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_mline)
            self.vertices = MLineVertices(tags)
        return dxf

    def preprocess_export(self, tagwriter: 'TagWriter') -> bool:
        # do not export MLines without vertices
        return bool(len(self.vertices))

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_mline.name)
        self.dxf.export_dxf_attribs(tagwriter, acdb_mline.attribs.keys())
        self.vertices.export_dxf(tagwriter)


acdb_mline_style = DefSubclass('AcDbMlineStyle', {
    'name': DXFAttr(2, default='Standard'),
    'flags': DXFAttr(70, default=0),  # Flags (bit-coded):
    # 1 =Fill on
    # 2 = Display miters
    # 16 = Start square end (line) cap
    # 32 = Start inner arcs cap
    # 64 = Start round (outer arcs) cap
    # 256 = End square (line) cap
    # 512 = End inner arcs cap
    # 1024 = End round (outer arcs) cap
    'description': DXFAttr(3, default=''),  # Style description (string, 255 characters maximum)
    'fill_color': DXFAttr(62, default=256),  # Fill color (integer, default = 256)
    'start_angle': DXFAttr(51, default=90),  # Start angle (real, default is 90 degrees)
    'end_angle': DXFAttr(52, default=90),  # End angle (real, default is 90 degrees)
    # 71: Number of elements
    # 49: Element offset (real, no default). Multiple entries can exist; one entry for each element
    # 62: Element color (integer, default = 0). Multiple entries can exist; one entry for each element
    # 6: Element linetype (string, default = BYLAYER). Multiple entries can exist; one entry for each element
})

MLineStyleElement = namedtuple('MLineStyleElement', 'offset color linetype')


class MLineStyleElements:
    def __init__(self, tags: Tags = None):
        self.elements = []  # type: List[MLineStyleElement]
        if tags:
            for e in self.parse_tags(tags):
                data = MLineStyleElement(e.get('offset', 1.), e.get('color', 0), e.get('linetype', 'BYLAYER'))
                self.elements.append(data)

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, item):
        return self.elements[item]

    def export_dxf(self, tagwriter: 'TagWriter'):
        write_tag = tagwriter.write_tag2
        write_tag(71, len(self.elements))
        for offset, color, linetype in self.elements:
            write_tag(49, offset)
            write_tag(62, color)
            write_tag(6, linetype)

    def append(self, offset: float, color: int = 0, linetype: str = 'BYLAYER') -> None:
        self.elements.append(MLineStyleElement(offset, color, linetype))

    @staticmethod
    def parse_tags(tags: Tags) -> Iterable[Dict]:
        collector = None
        for code, value in tags:
            if code == 49:
                if collector is not None:
                    yield collector
                collector = {'offset': value}
            elif code == 62:
                collector['color'] = value
            elif code == 6:
                collector['linetype'] = value
        if collector is not None:
            yield collector


@register_entity
class MLineStyle(DXFObject):
    DXFTYPE = 'MLINESTYLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_mline_style)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.elements = MLineStyleElements()

    def copy(self):
        raise DXFTypeError('Copying of MLINESTYLE not supported.')

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_mline_style)
        self.elements = MLineStyleElements(tags)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_mline_style.name)
        self.dxf.export_dxf_attribs(tagwriter, acdb_mline_style.attribs.keys())
        self.elements.export_dxf(tagwriter)


class MLineStyleCollection(ObjectCollection):
    def __init__(self, doc: 'Drawing'):
        super().__init__(doc, dict_name='ACAD_MLINESTYLE', object_type='MLINESTYLE')
        self.create_required_entries()

    def create_required_entries(self) -> None:
        if 'Standard' not in self.object_dict:
            entity = self.new('Standard')  # type: MLineStyle
            entity.elements.append(.5, 256)
            entity.elements.append(-.5, 256)
