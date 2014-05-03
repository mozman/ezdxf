# Purpose: blocks section
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice

from .tags import TagGroups, DXFStructureError
from .classifiedtags import ClassifiedTags, get_tags_linker
from . import const


class BlocksSection(object):
    name = 'blocks'

    def __init__(self, tags, drawing):
        # Mapping of BlockLayouts, key is BlockLayout.name, for dict() order of blocks is random,
        # if turns out later, that blocks order is important: use an OrderedDict().
        self._block_layouts = dict()
        self.drawing = drawing
        if tags is not None:
            self._build(tags)
        self._anonymous_block_counter = 0

    def __len__(self):
        return len(self._block_layouts)

    @property
    def entitydb(self):
        return self.drawing.entitydb

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    def _build(self, tags):
        def add_tags(tags):
            return self.entitydb.add_tags(tags)

        def build_block_layout(entities):
            linked_tags = get_tags_linker()
            tail_handle = add_tags(entities.pop())
            entities_iterator = iter(entities)
            head_handle = add_tags(next(entities_iterator))
            block = self.dxffactory.new_block_layout(head_handle, tail_handle)

            for entity in entities_iterator:
                handle = add_tags(entity)
                if not linked_tags(entity):  # also creates the link structure as side effect
                    block.add_handle(handle)
            return block

        if tags[0] != (0, 'SECTION') or \
            tags[1] != (2, 'BLOCKS') or \
            tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in BLOCKS section.")

        if len(tags) == 3:  # empty block section
            return

        entities = []
        fix_tags = self.dxffactory.fix_tags
        for group in TagGroups(islice(tags, 2, len(tags) - 1)):
            tags = ClassifiedTags(group)
            fix_tags(tags)  # post read tags fixer for VERTEX!
            entities.append(tags)
            if group[0].value == 'ENDBLK':
                self.add(build_block_layout(entities))
                entities = []

    def add(self, block_layout):
        """ Add or replace a BlockLayout() object.
        """
        self._block_layouts[block_layout.name] = block_layout

    # start of public interface

    def __iter__(self):
        return iter(self._block_layouts.values())

    def __contains__(self, entity):
        try:
            name = entity.name
        except AttributeError:
            name = entity
        return name in self._block_layouts

    def __getitem__(self, name):
        return self._block_layouts[name]

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
        head = self.dxffactory.create_db_entry('BLOCK', dxfattribs)
        tail = self.dxffactory.create_db_entry('ENDBLK', {})
        block_layout = self.dxffactory.new_block_layout(head.dxf.handle, tail.dxf.handle)
        self.dxffactory.create_block_entry_in_block_records_table(block_layout)
        self.add(block_layout)
        return block_layout

    def new_anonymous_block(self, type_char='U', base_point=(0, 0)):
        blockname = self.anonymous_blockname(type_char)
        block = self.new(blockname, base_point, {'flags': const.BLK_ANONYMOUS})
        return block

    def anonymous_blockname(self, type_char):
        """ Create name for an anonymous block.

        type_char
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

    def delete_block(self, name):
        block_layout = self[name]
        block_layout.destroy()
        del self._block_layouts[name]

    def delete_all_blocks(self):
        # do not delete blocks defined for layouts
        if self.drawing.dxfversion != 'AC1009':
            layout_keys = set(layout.layout_key for layout in self.drawing.layouts)
            for block in list(self):
                if block.get_block_record_handle() not in layout_keys:
                    self.delete_block(block.name)
        else:
            for block_name in list(self._block_layouts.keys()):
                if block_name not in ('$MODEL_SPACE', '$PAPER_SPACE'):
                    self.delete_block(block_name)

    # end of public interface

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\nBLOCKS\n")
        for block in self._block_layouts.values():
            block.write(stream)
        stream.write("  0\nENDSEC\n")

    def new_paper_space_block(self):

        def block_name():
            return "*Paper_Space%d" % count

        count = 1
        while block_name() in self._block_layouts:
            count += 1

        block_layout = self.new(block_name())
        return block_layout.get_block_record_handle()