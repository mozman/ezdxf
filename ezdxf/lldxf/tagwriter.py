# Purpose: tag writer
# Created: 13.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import CompressedTags
from .types import strtag2, TAG_STRING_FORMAT


class TagWriter(object):
    """
    Writes DXF tags into a stream.

    Args:
        stream: text stream
        write_handles: if False don't write handles (5, 105), use only for DXF R12 format

    """
    def __init__(self, stream, write_handles=True):
        self._stream = stream
        self._write_handles = write_handles

    def write_tags(self, tags):
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

    def write_tag(self, tag):
        if isinstance(tag, CompressedTags):
            s = tag.tostring()
        else:
            s = strtag2(tag)
        self._stream.write(s)

    def write_tag2(self, code, value):
        self._stream.write(TAG_STRING_FORMAT % (code, value))

    def write_str(self, s):
        self._stream.write(s)

