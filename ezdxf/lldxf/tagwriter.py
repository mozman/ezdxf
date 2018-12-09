# Created: 13.01.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from typing import Any, TextIO, TYPE_CHECKING, Union
from .types import TAG_STRING_FORMAT
from .tags import DXFTag

if TYPE_CHECKING:
    from ezdxf.lldxf.tags import Tags
    from ezdxf.lldxf.extendedtags import ExtendedTags


class TagWriter:
    """
    Writes DXF tags into a stream.

    Args:
        stream: text stream
        write_handles: if False don't write handles (5, 105), use only for DXF R12 format

    """

    def __init__(self, stream: TextIO, write_handles: bool = True):
        self._stream = stream
        self._write_handles = write_handles

    def write_tags(self, tags: Union['Tags', 'ExtendedTags']) -> None:
        if self._write_handles:
            for tag in tags:
                self.write_tag(tag)
        else:  # don't write handles
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
