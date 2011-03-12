#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: default chunk
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import TAG_STRING_FORMAT

class DefaultChunk:
    def __init__(self, tags, drawing):
        self.tags = tags
        self.drawing = drawing

    @property
    def dxfengine(self):
        return self.drawing.dxfengine

    @property
    def name(self):
        return self.tags[1].value.lower()

    def write(self, stream):
        for tag in self.tags:
            stream.write(TAG_STRING_FORMAT % tag)

def iterchunks(tagreader, stoptag='EOF', endofchunk='ENDSEC'):
    while True:
        tag = next(tagreader)
        if tag == (0, stoptag):
            return
        tags = [tag]
        while tag != (0, endofchunk):
            tag = next(tagreader)
            tags.append(tag)
        yield tags
