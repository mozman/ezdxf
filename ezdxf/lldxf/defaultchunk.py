# Purpose: default chunk
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import Tags, CompressedTags
from .const import COMPRESSED_TAGS


class DefaultChunk(object):
    def __init__(self, tags, drawing):
        self.tags = tags
        self._drawing = drawing

    @property
    def dxffactory(self):
        return self._drawing.dxffactory

    @property
    def name(self):
        return self.tags[1].value.lower()

    def write(self, stream):
        self.tags.write(stream)


class CompressedDefaultChunk(DefaultChunk):
    def __init__(self, tags, drawing):
        compressed_tags = CompressedTags(COMPRESSED_TAGS, tags)
        super(CompressedDefaultChunk, self).__init__(Tags((tags[0], tags[1], compressed_tags)), drawing)
        self._compressed_tags = compressed_tags

    def write(self, stream):
        self._compressed_tags.write(stream)


def iter_chunks(tagreader, stoptag='EOF', endofchunk='ENDSEC'):
    try:
        while True:
            tag = next(tagreader)
            if tag == (0, stoptag):
                return
            tags = Tags([tag])
            while tag != (0, endofchunk):
                tag = next(tagreader)
                tags.append(tag)
            yield tags
    except StopIteration:
        return
