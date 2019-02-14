# Created: 13.01.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from typing import Any, TextIO, TYPE_CHECKING, Union
from .types import TAG_STRING_FORMAT, cast_tag_value
from .tags import DXFTag, Tags
from .const import LATEST_DXF_VERSION

if TYPE_CHECKING:
    from ezdxf.eztypes import ExtendedTags


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

    def write_str(self, s: str) -> None:
        self._stream.write(s)


class TagCollector:
    """
    Collects DXF tags as DXFTag() entities for testing.

    """

    def __init__(self, dxfversion=LATEST_DXF_VERSION, write_handles: bool = True):
        self.tags = []
        self.dxfversion = dxfversion
        self.write_handles = write_handles  # flag is needed for new new entity structure!

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

    def write_str(self, s: str) -> None:
        self.write_tags(Tags.from_text(s))
