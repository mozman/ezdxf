# Purpose: Import data from another DXF drawing
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

from ezdxf.query import name_query


class Importer(object):
    def __init__(self, source, target, strict_mode=True):
        self.source = source  # type of: ezdxf.Drawing
        self.target = target  # type of: ezdxf.Drawing
        self._renamed_blocks = {}
        self._handle_translation_table = {}
        self._requires_data_from_objects_section = []
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
        # It is possible to copy an entity from a newer to an older versions, if the entity is defined for both versions
        # (like LINE, CIRCLE, ...), but this can not be granted by default. Enable this feature by
        # Importer(s, t, strict_mode=False).
        return False

    def import_all(self, table_conflict="discard", block_conflict="discard"):
        self.import_tables(conflict=table_conflict)
        self.import_blocks(conflict=block_conflict)
        self.import_modelspace_entities()
        self.import_required_data_from_objects_section()

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
            self.entity_post_processing(new_entity)

    def entity_post_processing(self, dxf_entity):
            dxftype = dxf_entity.dxftype()
            if dxftype == "INSERT":
                self.resolve_block_ref(dxf_entity)
            elif dxftype == 'IMAGE':
                self._requires_data_from_objects_section.append(dxf_entity)

    def resolve_block_ref(self, block_ref):
        old_block_name = block_ref.dxf.name
        new_block_name = self._renamed_blocks.get(old_block_name, old_block_name)
        block_ref.dxf.name = new_block_name

    def import_blocks(self, query="*", conflict="discard"):
        """ Import block definitions.

        :param str query: names of blocks to import, "*" for all
        :param str conflict: discard|replace|rename
        """
        has_block_records = self.target.dxfversion > 'AC1009'

        def import_block_record(block_layout):
            if not has_block_records:
                return
            block_record_handle = block_layout.block_record_handle
            if block_record_handle != '0':
                block_record_handle = self.import_tags(block_record_handle)
                self.target.sections.tables.block_records._append_entry_handle(block_record_handle)
                block_layout.set_block_record_handle(block_record_handle)
                block_record = self.target.dxffactory.wrap_handle(block_record_handle)
                _cleanup_block_record(block_record)

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
            rename_block_record(block)
            existing_block_names.add(new_name)
            self._renamed_blocks[old_name] = new_name

        def rename_block_record(block_layout):
            if not has_block_records:
                return
            block_record_handle = block_layout.block_record_handle
            if block_record_handle != '0':
                block_record = self.target.dxffactory.wrap_handle(block_record_handle)
                block_record.dxf.name = block_layout.name

        def import_block_layout(source_block_layout):
            head_handle = self.import_tags(source_block_layout._block_handle)
            tail_handle = self.import_tags(source_block_layout._endblk_handle)
            target_block_layout = self.target.dxffactory.new_block_layout(head_handle, tail_handle)
            import_block_record(target_block_layout)
            import_block_entities(source_block_layout, target_block_layout)
            return target_block_layout

        def import_block_entities(source_block_layout, target_block_layout):
            for entity in source_block_layout:
                target_handle = self.import_tags(entity.dxf.handle)
                new_entity = self.target.dxffactory.wrap_handle(target_handle)
                target_block_layout.add_entity(new_entity)
                dxftype = new_entity.dxftype()
                if dxftype == 'INSERT':  # maybe a reference to a renamed block
                    resolve_block_references.append(new_entity)
                elif dxftype == 'IMAGE':
                    self._requires_data_from_objects_section.append(new_entity)

        resolve_block_references = []
        existing_block_names = set(block.name for block in self.target.blocks)
        # Do not import blocks associated to layouts and model space
        layout_block_names = frozenset(_get_layout_block_names(self.source))
        block_names_without_layouts = frozenset(block.name for block in self.source.blocks) - layout_block_names
        import_block_names = frozenset(name_query(block_names_without_layouts, query))

        for block in self.source.blocks:  # blocks is a list, access by blocks[name] is slow
            block_name = block.name
            if block_name not in import_block_names:
                continue
            if block_name not in existing_block_names:
                target_block_layout = import_block_layout(block)
                self.target.blocks.add(target_block_layout)
            else:  # we have a name conflict
                if conflict == 'discard':
                    continue
                elif conflict == 'rename':
                    target_block_layout = import_block_layout(block)
                    rename(target_block_layout)
                    self.target.blocks.add(target_block_layout)
                elif conflict == 'replace':
                    target_block_layout = import_block_layout(block)
                    self.target.blocks.add(target_block_layout)
                else:
                    raise ValueError("'{}' is an invalid value for parameter conflict.".format(conflict))

        # update renamed block names
        for block_ref in resolve_block_references:
            self.resolve_block_ref(block_ref)

    def import_tables(self, query="*", conflict="discard"):
        """ Import table entries.

        :param str conflict: discard|replace
        """
        table_names = [table.name for table in self.source.sections.tables if table.name != 'block_records']
        for table_name in name_query(table_names, query):
            self.import_table(table_name, query="*", conflict=conflict)

    def import_table(self, name, query="*", conflict="discard"):
        """ Import specific entries from a table.

        :param str name: valid table names are 'layers', 'linetypes', 'appids', 'dimstyles',
                         'styles', 'ucs', 'views', 'viewports' except 'block_records'
                         as defined in ezdxf.table.TABLENAMES

        :param str conflict: discard|replace
        """
        if conflict not in ('replace', 'discard'):
            raise ValueError("Unknown value '{}' for parameter 'conflict'.".format(conflict))
        if name == 'block_records':
            raise ValueError("Can not import whole block_records table, block_records will be imported as required.")
        try:
            source_table = self.source.sections.tables[name]
        except KeyError:
            raise ValueError("Source drawing has no table '{}'.".format(name))
        try:
            target_table = self.target.sections.tables[name]
        except KeyError:
            raise ValueError("Table '{}' does not exists in the target drawing. "
                             "Table creation in the target drawing not implemented yet!".format(name))
        source_entry_names = (entry.dxf.name for entry in source_table)
        for entry_name in name_query(source_entry_names, query):
            table_entry = source_table.get(entry_name)
            if table_entry.dxf.name in target_table:
                if conflict == 'discard':
                    continue
                else:  # replace existing entry
                    target_table.remove(table_entry.dxf.name)
            new_handle = self.import_tags(table_entry.dxf.handle)
            target_table._append_entry_handle(new_handle)

    def import_tags(self, source_handle):
        """Clone tags from source drawing, give it a new valid handle for the target drawing
        and insert tags into the entity database of the target drawing. Returns the target handle.
        Avoids duplicate imports of the same database entity.
        """
        source_db = self.source.entitydb
        target_db = self.target.entitydb
        next_target_handle = self.target._handles.next

        def clone_tags(source_handle):
            new_tags = source_db[source_handle].clone()
            target_handle = next_target_handle()
            new_tags.replace_handle(target_handle)
            target_db[target_handle] = new_tags
            self._handle_translation_table[source_handle] = target_handle
            return target_handle, new_tags

        main_target_handle = self._handle_translation_table.get(source_handle, None)
        prev_tags = None

        if main_target_handle is None:
            while True:
                target_handle, new_tags = clone_tags(source_handle)
                if main_target_handle is None:  # just the first tag list is relevant
                    main_target_handle = target_handle

                if prev_tags is not None:
                    prev_tags.link = target_handle

                if new_tags.link is None:
                    break
                else:  # clone linked tags
                    source_handle = new_tags.link
                    prev_tags = new_tags

        return main_target_handle

    def import_required_data_from_objects_section(self):  # TODO
        for entity in self._requires_data_from_objects_section:
            # for IMAGE import IMAGE_DEF
            pass


def _cleanup_block_record(block_record):
    def remove_tags(tags, code):
        del_tags = [tag for tag in tags if tag.code == code]
        for tag in del_tags:
            tags.remove(tag)

    if hasattr(block_record.tags, 'get_app_data'):
        try:  # BLKREFS are invalid handles to INSERT entities in the source drawing
            block_refs = block_record.tags.get_app_data("{BLKREFS")
        except ValueError:  # has no block references
            pass
        else:
            remove_tags(block_refs, 331)
        # strip preview image and save space
        subclass = block_record.tags.get_subclass('AcDbBlockTableRecord')
        remove_tags(subclass, 310)


def _get_layout_block_names(dwg):
    def get_block_record_name(layout):
        block_record = dwg.dxffactory.wrap_handle(layout._block_record_handle)
        return block_record.dxf.name

    if dwg.dxfversion <= 'AC1009':
        return '$MODEL_SPACE', '$PAPER_SPACE'
    return (get_block_record_name(layout) for layout in dwg.layouts)
