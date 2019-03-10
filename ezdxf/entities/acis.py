# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-03-09
from typing import TYPE_CHECKING, Iterable, List, Union
from contextlib import contextmanager
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXFTypeError, DXF2013
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
    'flags': DXFAttr(290, dxfversion=DXF2013),
    'uid': DXFAttr(2, dxfversion=DXF2013),
})

# with R2013/AC1027 Modeler Geometry of ACIS data is stored in the ACDSDATA section as binary encoded information
# detection:
# group code 70, 1, 3 is missing
# group code 290, 2 present
#
#   0
# ACDSRECORD
#  90
# 1
#   2
# AcDbDs::ID
# 280
# 10
# 320
# 19B   <<< handle of associated 3DSOLID entity in model space
#   2
# ASM_Data
# 280
# 15
#  94
# 7197  <<< size in bytes ???
# 310
# 414349532042696E61727946696C6...


@register_entity
class Body(DXFGraphic):
    """ DXF BODY entity - container entity for embedded ACIS data. """
    DXFTYPE = 'BODY'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_modeler_geometry)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._acis_data = []  # type: List[Union[str, bytes]]

    @property
    def acis_data(self) -> List[Union[str, bytes]]:
        """ Get ACIS text data as list of strings for DXF R2000 to DXF R2010 and binary encoded ACIS data for DXF R2013
        and later as list of bytes.
        """
        if self.has_binary_data:
            return self.doc.acdsdata.get_acis_data(self.dxf.handle)
        else:
            return self._acis_data

    @acis_data.setter
    def acis_data(self, lines: Iterable[str]):
        """ Set ACIS data as list of strings for DXF R2000 to DXF R2010. In case of DXF R2013 and later, setting ACIS
        data as binary data is not supported.
        """
        if self.has_binary_data:
            raise DXFTypeError('Setting ACIS data not supported for DXF R2013 and later.')
        else:
            self._acis_data = list(lines)

    @property
    def has_binary_data(self):
        return self.doc.dxfversion >= DXF2013

    def copy(self):
        raise DXFTypeError('Copying of ACIS data not supported.')

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.load_dxfattribs_into_namespace(dxf, acdb_modeler_geometry)
            if not self.has_binary_data:
                self.load_acis_data(processor.subclasses[2])
        return dxf

    def load_acis_data(self, tags: Tags):
        text_lines = tags2textlines(tag for tag in tags if tag.code in (1, 3))
        self.acis_data = crypt.decode(text_lines)

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_modeler_geometry.name)
        if tagwriter.dxfversion >= DXF2013:
            # ACIS data stored in the ACDSDATA section as binary encoded information
            if self.dxf.hasattr('version'):
                tagwriter.write_tag2(70, self.dxf.version)
            self.dxf.export_dxf_attribs(tagwriter, ['flags', 'uid'])
        else:
            # DXF R2000 - R2013 stores ACIS data as text in entity
            self.dxf.export_dxf_attribs(tagwriter, 'version')
            self.export_acis_data(tagwriter)

    def export_acis_data(self, tagwriter: 'TagWriter') -> None:
        def cleanup(lines):
            for line in lines:
                yield line.rstrip().replace('\n', '')

        tags = Tags(textlines2tags(crypt.encode(cleanup(self.acis_data))))
        tagwriter.write_tags(tags)

    def set_text(self, text: str, sep: str = '\n') -> None:
        """ Set ACIS data from one string. """
        self.acis_data = text.split(sep)

    def tostring(self) -> str:
        """ Returns ACIS data as one string for DXF R2000 - R2010. """
        if self.has_binary_data:
            return ""
        else:
            return "\n".join(self.acis_data)

    def tobytes(self) -> bytes:
        """ Returns ACIS data as joined bytes for DXF R2013 and later. """
        if self.has_binary_data:
            return b"".join(self.acis_data)
        else:
            return b""

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


def tags2textlines(tags: Iterable) -> Iterable[str]:
    """ Yields text lines from code 1 and 3 tags, code 1 starts a line following code 3 tags are appended to the line.
    """
    line = None
    for code, value in tags:
        if code == 1:
            if line is not None:
                yield line
            line = value
        elif code == 3:
            line += value
    if line is not None:
        yield line


def textlines2tags(lines: Iterable[str]) -> Iterable[DXFTag]:
    """ Yields text lines as DXFTags, splitting long lines (>255) int code 1 and code 3 tags.
    """
    for line in lines:
        text = line[:255]
        tail = line[255:]
        yield DXFTag(1, text)
        while len(tail):
            text = tail[:255]
            tail = tail[255:]
            yield DXFTag(3, text)


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

