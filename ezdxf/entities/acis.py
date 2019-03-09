# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-03-09
from typing import TYPE_CHECKING, Iterable, List
from contextlib import contextmanager
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXFTypeError
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.tools import crypt
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, DXFNamespace, Drawing

__all__ = ['Body']

acdb_modeler_geometry = DefSubclass('AcDbModelerGeometry', {
    'version': DXFAttr(70, default=1),
})


@register_entity
class Body(DXFGraphic):
    """ DXF BODY entity - container entity for embedded ACIS data. """
    DXFTYPE = 'BODY'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_modeler_geometry)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._acis_data = []  # type: List[str]

    @property
    def acis_data(self) -> List[str]:
        """ Get ACIS data as list of strings. """
        return self._acis_data

    @acis_data.setter
    def acis_data(self, lines: Iterable[str]):
        """ Set ACIS data as list of strings. """
        self._acis_data = list(lines)

    def copy(self):
        raise DXFTypeError('Copying of ACIS data not supported.')

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.load_dxfattribs_into_namespace(dxf, acdb_modeler_geometry)
            self.load_acsi_data(processor.subclasses[2])
        return dxf

    def load_acis_data(self, tags: Tags):
        text_lines = convert_tags_to_text_lines(tag for tag in tags if tag.code in (1, 3))
        self.acis_data = crypt.decode(text_lines)

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_modeler_geometry.name)
        self.dxf.export_dxf_attribs(tagwriter, 'version')
        self.export_acis_data(tagwriter)

    def export_acis_data(self, tagwriter: 'TagWriter') -> None:
        def cleanup(lines):
            for line in lines:
                yield line.rstrip().replace('\n', '')

        tags = Tags(convert_text_lines_to_tags(crypt.encode(cleanup(self.acis_data))))
        tagwriter.write_tags(tags)

    def set_text(self, text: str, sep: str = '\n') -> None:
        """ Set ACIS data from one string. """
        self.acis_data = text.split(sep)

    def tostring(self) -> str:
        """ Returns ACIS data as one string. """
        return "\n".join(self.acis_data)

    def get_acis_data(self):
        # for backward compatibility
        return self.acis_data

    def set_acis_data(self, text_lines: Iterable[str]) -> None:
        # for backward compatibility
        self.acis_data = text_lines

    @contextmanager
    def edit_data(self) -> 'ModelerGeometry':
        # for backward compatibility
        data = ModelerGeometry(self)
        yield data
        self.acis_data = data.text_lines


class ModelerGeometry:
    # for backward compatibility
    def __init__(self, body: 'Body'):
        self.text_lines = body.acis_data

    def __str__(self) -> str:
        return "\n".join(self.text_lines)

    def set_text(self, text: str, sep: str = '\n') -> None:
        self.text_lines = text.split(sep)


def convert_tags_to_text_lines(line_tags: Iterable[DXFTag]) -> Iterable[str]:
    """
    Args:
        line_tags: tags with code 1 or 3, tag with code 3 is the tail of previous line with more than 255 chars.

    Returns: yield strings

    """
    line_tags = iter(line_tags)
    try:
        line = next(line_tags).value  # raises StopIteration
    except StopIteration:
        return
    while True:
        try:
            tag = next(line_tags)
        except StopIteration:
            if line:
                yield line
            return
        if tag.code == 3:
            line += tag.value
            continue
        yield line
        line = tag.value


def convert_text_lines_to_tags(text_lines: Iterable[str]) -> Iterable[DXFTag]:
    for line in text_lines:
        yield DXFTag(1, line[:255])
        if len(line) > 255:
            yield DXFTag(3, line[255:])  # tail (max. 255 chars), what if line > 510 chars???


@register_entity
class Region(Body):
    """ DXF REGION entity - container entity for embedded ACIS data. """
    DXFTYPE = 'REGION'


acdb_3dsolid = DefSubclass('AcDb3dSolid', {
    'history_handle': DXFAttr(350, default='0'),
})


@register_entity
class Solid3d(Body):
    """ DXF 3DSOLID entity - container entity for embedded ACIS data. """
    DXFTYPE = '3DSOLID'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_modeler_geometry, acdb_3dsolid)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.load_dxfattribs_into_namespace(dxf, acdb_3dsolid)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_3dsolid.name)
        self.dxf.export_dxf_attribs(tagwriter, 'history_handle')

