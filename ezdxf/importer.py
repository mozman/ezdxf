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
            new_entry_tags = entity.tags.clone()  # create a new tag list
            handle = new_handle()
            new_entry_tags.replace_handle(handle)
            self.target.entitydb[handle] = new_entry_tags  # add tag list to entity database
            new_entity = self.target.dxffactory.wrap_entity(new_entry_tags)
            target_modelspace.add_entity(new_entity)  # add entity to modelspace
            if new_entity.dxftype() == "INSERT":
                self.resolve_block_ref(new_entity)

    def resolve_block_ref(self, block_ref):
        old_block_name = block_ref.dxf.name
        new_block_name = self._renamed_blocks.get(old_block_name, old_block_name)
        block_ref.dxf.name = new_block_name
        block_ref.dxf.name2 = new_block_name

    def import_blocks(self, query="*", conflict="discard"):
        """ Import block definitions.

        :param str query: names of blocks to import, "*" for all
        :param str conflict: discard|replace|rename
        """
        # TODO: import associated block_references, if necessary
        def rename(block):
            counter = 1
            old_name = block.name
            while True:
                new_name = old_name + "_%d" % counter
                if new_name in existing_block_names:
                    counter += 1
                else:
                    block.name = new_name
                    break
            existing_block_names.add(new_name)
            self._renamed_blocks[old_name] = new_name

        def new_block_layout(source_block_layout):
            def copy_entity(source_handle):
                new_tags = self.source.entitydb[source_handle].clone()
                target_handle = self.target._handles.next()
                new_tags.replace_handle(target_handle)
                self.target.entitydb[target_handle] = new_tags
                return target_handle

            head_handle = copy_entity(source_block_layout._block_handle)
            tail_handle = copy_entity(source_block_layout._endblk_handle)
            target_block_layout = self.target.dxffactory.new_block_layout(head_handle, tail_handle)
            for entity in source_block_layout:
                target_handle = copy_entity(entity.handle())
                new_entity = self.target.dxffactory.wrap_handle(target_handle)
                target_block_layout.add_entity(new_entity)
                if new_entity.dxftype() == 'INSERT':  # maybe a reference to a renamed block
                    resolve_block_references.append(new_entity)
            return target_block_layout

        resolve_block_references = []
        existing_block_names = set(block.name for block in self.target.blocks)
        import_block_names = frozenset(name_query((block.name for block in self.source.blocks), query))
        for block in self.source.blocks:  # blocks are a list, access by blocks[name] is slow
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

        # update renamed block names
        for block_ref in resolve_block_references:
            self.resolve_block_ref(block_ref)

    def import_tables(self, query="*", conflict="discard"):
        """ Import table entries.

        :param str conflict: discard|replace
        """
        table_names = [table.name for table in self.source.sections.tables]
        for table_name in name_query(table_names, query):
            self.import_table(table_name, query="*", conflict=conflict)

    def import_table(self, name, query="*", conflict="discard"):
        """ Import specific entries from a table.

        :param str name: valid table names are 'layers', 'linetypes', 'appids', 'dimstyles',
                         'styles', 'ucs', 'views', 'viewports' and 'block_records'
                         as defined in ezdxf.table.TABLENAMES

        :param str conflict: discard|replace
        """
        if conflict not in ('replace', 'discard'):
            raise ValueError("Unknown value '{}' for parameter 'conflict'.".format(conflict))
        
        try:
            source_table = self.source.sections.tables[name]
        except KeyError:
            raise ValueError("Source drawing has no table '{}'.".format(name))
        try:
            target_table = self.target.sections.tables[name]
        except KeyError:
            raise ValueError("Table '{}' does not exists in the target drawing. "
                             "Table creation in the target drawing not implemented yet!".format[name])
        new_handle = self.target._handles.next
        source_entry_names = (entry.dxf.name for entry in source_table)
        for entry_name in name_query(source_entry_names, query):
            table_entry = source_table.get(entry_name)
            if table_entry.dxf.name in target_table:
                if conflict == 'discard':
                    continue
                else: # replace existing entry
                    target_table.remove(table_entry.dxf.name)
            new_entry_tags = table_entry.tags.clone()
            new_entry_tags.replace_handle(new_handle())
            target_table._add_entry(new_entry_tags)
