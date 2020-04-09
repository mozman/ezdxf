# Created: 13.01.2018
# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import Any, TextIO, TYPE_CHECKING, Union, List, Iterable, BinaryIO
from .types import TAG_STRING_FORMAT, cast_tag_value
from .types import BYTES, INT16, INT32, INT64, DOUBLE, BINARY_CHUNK
from .tags import DXFTag, Tags
from .const import LATEST_DXF_VERSION
from ezdxf.tools import take2
import struct

if TYPE_CHECKING:
    from ezdxf.eztypes import ExtendedTags, DXFEntity

__all__ = ['TagWriter', 'TagCollector', 'basic_tags_from_text']


class TagWriter:
    """
    Writes DXF tags into a stream.

    Args:
        stream: text stream
        write_handles: if False don't write handles (5, 105), use only for DXF R12 format

    """

    def __init__(self, stream: TextIO, dxfversion=LATEST_DXF_VERSION, write_handles: bool = True):
        self._stream = stream
        # this are just options for export functions
        self.dxfversion = dxfversion
        self.write_handles = write_handles  # flag is needed for new new entity structure!
        # force writing optional values if equal to default value when set
        # True is only used for testing
        self.force_optional = False

    def write_tags(self, tags: Union['Tags', 'ExtendedTags']) -> None:
        for tag in tags:
            self.write_tag(tag)

    def write_tag(self, tag: DXFTag) -> None:
        self._stream.write(tag.dxfstr())

    def write_tag2(self, code: int, value: Any) -> None:
        self._stream.write(TAG_STRING_FORMAT % (code, value))

    def write_vertex(self, code: int, vertex: Iterable[float]) -> None:
        for index, value in enumerate(vertex):
            self.write_tag2(code + index * 10, value)

    def write_str(self, s: str) -> None:
        self._stream.write(s)


class BinaryTagWriter(TagWriter):
    """
    Writes binary encoded DXF tags into a binary stream.

    Args:
        stream: binary IO stream
        write_handles: if ``False`` don't write handles (5, 105), use only for DXF R12 format

    """

    def __init__(self, stream: BinaryIO, dxfversion=LATEST_DXF_VERSION, write_handles: bool = True, encoding='utf8'):
        super().__init__(None, dxfversion, write_handles)
        self._stream = stream
        self._encoding = encoding  # output encoding
        self._one_byte_group_code = self.dxfversion <= 'AC1009'

    def write_signature(self) -> None:
        self._stream.write(b'AutoCAD Binary DXF\r\n\x1a\x00')

    def write_tags(self, tags: Union['Tags', 'ExtendedTags']) -> None:
        for tag in tags:
            self.write_tag2(tag.code, tag.value)

    def write_tag(self, tag: DXFTag) -> None:
        self.write_tag2(tag.code, tag.value)

    def write_str(self, s: str) -> None:
        data = s.split('\n')
        for code, value in take2(data):
            self.write_tag2(int(code), value)

    def write_tag2(self, code: int, value: Any) -> None:
        # Binary DXF files do not support comments!
        assert code != 999
        stream = self._stream

        if code >= 1000:  # extended data
            stream.write(b'\xff')
            stream.write(code.to_bytes(2, 'little'))
        else:
            sz = 1 if self._one_byte_group_code and code < 256 else 2
            stream.write(code.to_bytes(sz, 'little'))

        if code in BYTES:
            stream.write(int(value).to_bytes(1, 'little'))
        elif code in INT16:
            stream.write(int(value).to_bytes(2, 'little', signed=True))
        elif code in INT32:
            stream.write(int(value).to_bytes(4, 'little', signed=True))
        elif code in INT64:
            stream.write(int(value).to_bytes(8, 'little', signed=True))
        elif code in DOUBLE:
            stream.write(struct.pack('<d', float(value)))
        elif code in BINARY_CHUNK:
            stream.write(len(value).to_bytes(1, 'little'))
            stream.write(value)
        else:  # String
            stream.write(str(value).encode(self._encoding))
            stream.write(b'\x00')


class TagCollector:
    """
    Collects DXF tags as DXFTag() entities for testing.

    """

    def __init__(self, dxfversion=LATEST_DXF_VERSION, write_handles: bool = True, optional: bool = True):
        self.tags = []
        self.dxfversion = dxfversion
        self.write_handles = write_handles  # flag is needed for new new entity structure!
        # force writing optional values if equal to default value when set
        # True is only used for testing
        self.force_optional = optional

    def write_tags(self, tags: Union['Tags', 'ExtendedTags']) -> None:
        for tag in tags:
            self.write_tag(tag)

    def write_tag(self, tag: DXFTag) -> None:
        if hasattr(tag, 'dxftags'):
            self.tags.extend(tag.dxftags())
        else:
            self.tags.append(tag)

    def write_tag2(self, code: int, value: Any) -> None:
        self.tags.append(DXFTag(code, cast_tag_value(int(code), value)))

    def write_vertex(self, code: int, vertex: Iterable[float]) -> None:
        for index, value in enumerate(vertex):
            self.write_tag2(code + index * 10, value)

    def write_str(self, s: str) -> None:
        self.write_tags(Tags.from_text(s))

    def has_all_tags(self, other: 'TagCollector'):
        return all(tag in self.tags for tag in other.tags)

    def reset(self):
        self.tags = []

    @classmethod
    def dxftags(cls, entity: 'DXFEntity', dxfversion=LATEST_DXF_VERSION):
        collector = cls(dxfversion=dxfversion)
        entity.export_dxf(collector)
        return Tags(collector.tags)


def basic_tags_from_text(text: str) -> List[DXFTag]:
    """
    Returns all tags from `text` as basic DXFTags(). All complex tags are resolved into basic (code, value) tags
    (e.g. DXFVertex(10, (1, 2, 3)) -> DXFTag(10, 1), DXFTag(20, 2), DXFTag(30, 3).

    Args:
        text: DXF data as string

    Returns: List of basic DXF tags (code, value)

    """
    collector = TagCollector()
    collector.write_tags(Tags.from_text(text))
    return collector.tags
