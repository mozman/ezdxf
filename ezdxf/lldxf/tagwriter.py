# Created: 13.01.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from typing import Any, TextIO, TYPE_CHECKING, Union, List, Iterable
from .types import TAG_STRING_FORMAT, cast_tag_value
from .tags import DXFTag, Tags
from .const import LATEST_DXF_VERSION

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
        if self.write_handles:
            for tag in tags:
                self.write_tag(tag)
        else:  # don't write handles todo: not needed for new entity structure, handled by entity itself at export
            if tags[0] == (0, 'DIMSTYLE'):
                handle_code = 105
            else:
                handle_code = 5
            for tag in tags:
                if tag.code == handle_code:
                    continue  # skip handles in DXF R12 files, use only for DXF R12 files!!!
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
