# Purpose: blocks section
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice

from .tags import TagGroups
from .classifiedtags import ClassifiedTags
from . import const


class BlocksSection(object):
    name = 'blocks'

    def __init__(self, tags, drawing):
        ## TODO: _blocks could be a dict()
        self._blocks = list()
        self._entitydb = drawing.entitydb
        self._dxffactory = drawing.dxffactory
        if tags is not None:
            self._build(tags)
        self._anonymous_block_counter = 0

    def _build(self, tags):
        def add_tags(tags):
            return self._entitydb.add_tags(tags)

        def build_block_layout(entities):
            tail_handle = add_tags(entities.pop())
            iterentities = iter(entities)
            head_handle = add_tags(next(iterentities))
            block = self._dxffactory.new_block_layout(head_handle, tail_handle)
            for entity in iterentities:
                handle = add_tags(entity)
                block.add_handle(handle)
            return block

        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, 'BLOCKS')
        assert tags[-1] == (0, 'ENDSEC')

        if len(tags) == 3:  # empty block section
            return

        entities = []
        for group in TagGroups(islice(tags, 2, len(tags) - 1)):
            entities.append(ClassifiedTags(group))
            if group[0].value == 'ENDBLK':
                block_layout = build_block_layout(entities)
                self.append_block_layout(block_layout)
                entities = []

    def append_block_layout(self, block_layout):
        self._blocks.append(block_layout)

    def replace_or_append_block_layout(self, block_layout):
        """ Replace existing block layout or append new block layout.
        """
        new_layout_name = block_layout.name
        for index, layout in enumerate(self._blocks):
            if layout.name == new_layout_name:
                self._blocks[index] = block_layout
                return
        self.append_block_layout(block_layout)

    # start of public interface

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

    def new(self, name, base_point=(0, 0), dxfattribs=None):
        """ Create a new named block. """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['name'] = name
        dxfattribs['name2'] = name
        dxfattribs['base_point'] = base_point
        head = self._dxffactory.create_db_entry('BLOCK', dxfattribs)
        tail = self._dxffactory.create_db_entry('ENDBLK', {})
        block_layout = self._dxffactory.new_block_layout(head.dxf.handle, tail.dxf.handle)
        self._dxffactory.create_block_entry_in_block_records_table(block_layout)
        self.append_block_layout(block_layout)
        return block_layout

    def new_anonymous_block(self, type_char='U', base_point=(0, 0)):
        blockname = self.anonymous_blockname(type_char)
        block = self.new(blockname, base_point, {'flags': const.BLK_ANONYMOUS})
        return block

    def anonymous_blockname(self, type_char):
        """ Create name for an anonymous block.

        typechar
            U = *U### anonymous blocks
            E = *E### anonymous non-uniformly scaled blocks
            X = *X### anonymous hatches
            D = *D### anonymous dimensions
            A = *A### anonymous groups
        """
        while True:
            self._anonymous_block_counter += 1
            blockname = "*%s%d" % (type_char, self._anonymous_block_counter)
            if not self.__contains__(blockname):
                return blockname

    # end of public interface

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\nBLOCKS\n")
        for block in self._blocks:
            block.write(stream)
        stream.write("  0\nENDSEC\n")
