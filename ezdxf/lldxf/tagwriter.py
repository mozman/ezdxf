# Purpose: tag writer
# Created: 13.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import CompressedTags
from .types import strtag2, TAG_STRING_FORMAT
from .tagger import internal_tag_compiler


class TagWriter(object):
    def __init__(self, stream):
        self._stream = stream

    def write_tags(self, tags):
        for tag in tags:
            self.write_tag(tag)

    def write_tag(self, tag):
        if isinstance(tag, CompressedTags):
            self.write_tags(tag.decompress())
        else:
            self._stream.write(strtag2(tag))

    def write_tag2(self, code, value):
        self._stream.write(TAG_STRING_FORMAT % (code, value))

    def write_str(self, s):
        self.write_tags(internal_tag_compiler(s))

