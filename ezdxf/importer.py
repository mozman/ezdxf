# Purpose: Import data from another DXF drawing
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

from .query import name_query

class Importer(object):
    def __init__(self, source, target, strict_mode=True):
        self.source = source # type of: ezdxf.Drawing
        self.target = target # type of: ezdxf.Drawing
        self._renamed_blocks = {}
        if strict_mode and not self.is_compatible():
            raise TypeError("DXF drawings are not compatible. Source version {}; Target version {}".format(
                source.dxfversion, target.dxfversion))

    def is_compatible(self):
        if self.source.dxfversion == self.target.dxfversion:
            return True
        # The basic DXF structure has been changed with version AC1012 (AutoCAD R13)
        # It is not possible to copy from R12 to a newer version and
        # it is not possible to copy from R13 or a newer version to R12.
        if self.source.dxfversion == 'AC1009' or self.target.dxfversion == 'AC1009':
            return False
        # It is always possible to copy from older to newer versions (except R12).
        if self.target.dxfversion > self.source.dxfversion:
            return True
        # It is possible to copy from newer to older versions, if the entity is defined for both versions.
        # But this can not be granted by default. You can operate with that by __init__(s, t, strict_mode=False).
        return False

    def import_all(self, table_conflict="discard", block_conflict="discard"):
        self.import_tables(conflict=table_conflict)
        self.import_blocks(conflict=block_conflict)
        self.import_modelspace_entities()

    def import_modelspace_entities(self, query="*"):
        import_entities = self.source.modelspace().query(query)
        target_modelspace = self.target.modelspace()
        new_handle = self.target._handles.next
        for entity in import_entities:  # entity is GraphicEntity() or inherited
            if entity.dxftype == "INSERT":
                self.resolve_block_ref(entity)
            handle = new_handle()
            entity.dxf.handle = handle  # new handle is always required
            self.target.entitydb[handle] = entity.tags  # add tag list to entity database
            target_modelspace.add_entity(entity)  # add entity to modelspace

    def resolve_block_ref(self, block_ref):
        old_block_name = block_ref.dxf.name
        new_block_name = self._renamed_blocks.get(old_block_name, old_block_name)
        block_ref.dxf.name = new_block_name
        block_ref.dxf.name2 = new_block_name

    def import_blocks(self, query="*", conflict="discard"):
        """ Import block definitions.

        :param str query: name of blocks to import, "*" for all
        :param str conflict: discard|replace|rename
        """
        def rename(block):
            counter = 1
            old_name = block.name
            while True:
                new_name = old_name + "_%d" % counter
                if new_name in existing_block_names:
                    counter += 1
                else:
                    block.name = new_name
                    block.name2 = new_name
                    break
            existing_block_names.add(new_name)
            self._renamed_blocks[old_name: new_name]

        def wrap(handle):
            return self.source.dxffactory.wrap_handle(handle)

        def new_block_layout(source_block_layout):
            def move_entity(entity):
                entity.handle = new_handle()
                self.target.entitydb[entity.handle] = entity.tags
                return entity

            head = move_entity(wrap(source_block_layout._block_handle))
            tail = move_entity(wrap(source_block_layout._endblk_handle))
            target_block_layout = self.target.dxffactory.new_block_layout(head.handle, tail.handle)
            for entity in source_block_layout:
                move_entity(entity)
                target_block_layout.add_entity(entity)
            return target_block_layout


        new_handle = self.target._handles.next
        existing_block_names = set(block.name for block in self.target.blocks)
        import_block_names = frozenset(name_query((block.name for block in self.source.blocks), query))
        for block in self.source.blocks:
            block_name = block.name
            if block_name not in import_block_names:
                continue
            if block_name not in existing_block_names:
                target_block_layout = new_block_layout(block)
                self.target.blocks.append_block_layout(target_block_layout)
            else: # we have a name conflict
                if conflict == 'discard':
                    continue
                elif conflict == 'rename':
                    target_block_layout = new_block_layout(block)
                    rename(target_block_layout)
                    self.target.blocks.append_block_layout(target_block_layout)
                elif conflict == 'replace':
                    target_block_layout = new_block_layout(block)
                    self.target.blocks.replace_or_append_block_layout(target_block_layout)
                else:
                    raise ValueError("'{}' is an invalid value for parameter conflict.".format(conflict))

    def import_tables(self, query="*", conflict="discard"):
        """ Import table entries.

        :param str conflict: discard|replace
        """
        raise NotImplementedError()

    def import_table(self, name, query="*", conflict="discard"):
        """ Import specific entries from a table.

        :param str conflict: discard|replace
        """
        raise NotImplementedError()