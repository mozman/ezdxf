#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: blocks section
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from itertools import islice

from .tags import TagGroups, Tags, ExtendedTags, DXFStructureError
from .entityspace import EntitySpace

class BlocksSection:
    name = 'blocks'
    def __init__(self, tags, drawing):
        self._blocks = list()
        self._entitydb = drawing.entitydb
        self._dxffactory = drawing.dxffactory
        self._build(tags)

    def _build(self, tags):
        def build_block(entities):
            block = Block(self._entitydb)
            block.set_tail(entities.pop())
            iterentities = iter(entities)
            block.set_head(next(iterentities))
            for entity in iterentities:
                block.add(entity)
            return block

        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, 'BLOCKS')
        assert tags[-1] == (0, 'ENDSEC')

        if len(tags) == 3: # empty block section
            return

        entities = []
        for group in TagGroups(islice(tags, 2, len(tags)-1)):
            entities.append(ExtendedTags(group))
            if group[0].value == 'ENDBLK':
                self._blocks.append(build_block(entities))
                entities = []

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\nBLOCKS\n")
        for block in self._blocks:
            block.write(stream)
        stream.write("  0\nENDSEC\n")

class Block:
    def __init__(self, entitydb):
        self._entityspace = EntitySpace(entitydb)
        self._head = ExtendedTags()
        self._tail = ExtendedTags()

    def set_head(self, tags):
        self._head = tags

    def set_tail(self, tags):
        self._tail = tags

    def add(self, entity):
        self._entityspace.add(entity)

    def write(self, stream):
        self._head.write(stream)
        self._entityspace.write(stream)
        self._tail.write(stream)
