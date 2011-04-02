#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: blocks section
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from itertools import islice

from .tags import TagGroups, Tags, ExtendedTags, DXFStructureError

class BlocksSection:
    name = 'blocks'
    def __init__(self, tags, drawing):
        ## TODO: _blocks could be a dict()
        self._blocks = list()
        self._entitydb = drawing.entitydb
        self._dxffactory = drawing.dxffactory
        self._build(tags)

    def _build(self, tags):
        def add_tags(tags):
            return self._entitydb.add_tags(tags)

        def build_block_layout(entities):
            block = self._dxffactory.new_block_layout()
            block.set_tail(add_tags(entities.pop()))
            iterentities = iter(entities)
            block.set_head(add_tags(next(iterentities)))
            for entity in iterentities:
                block.add_entity(entity)
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
                block_layout = build_block_layout(entities)
                self._append_block_layout(block_layout)
                entities = []

    def _append_block_layout(self, block_layout):
        self._blocks.append(block_layout)

    # start public interface

    def __iter__(self):
        return iter(self._blocks)

    def __contains__(self, entity):
        try:
            name = entity.name
        except AttributeError:
            name = entity
        try:
            self.__getitem__(name)
            return True
        except KeyError:
            return False

    def __getitem__(self, name):
        for block in self:
            if name == block.name:
                return block
        raise KeyError(name)

    def get(self, name, default=None):
        try:
            return self.__getitem__(name)
        except KeyError:
            return default

    def new(self, name, basepoint=(0, 0), attribs={}):
        """ Create a new named block. """
        attribs['name'] = name
        attribs['name2'] = name
        attribs['basepoint'] = basepoint
        head = self._dxffactory.create_db_entry('BLOCK', attribs)
        tail = self._dxffactory.create_db_entry('ENDBLK', {})
        newblock = self._dxffactory.new_block_layout()
        newblock.set_head(head.handle)
        newblock.set_tail(tail.handle)
        self._append_block_layout(newblock)
        return newblock

    # start public interface

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\nBLOCKS\n")
        for block in self._blocks:
            block.write(stream)
        stream.write("  0\nENDSEC\n")
