# Purpose: Import data from another DXF drawing
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

class Importer(object):
    def __init__(self, source, target, strict_mode=True):
        self.source = source # type of: ezdxf.Drawing
        self.target = target # type of: ezdxf.Drawing
        if strict_mode and not self.is_compatible():
            raise TypeError("DXF drawings are not compatible. Source version {}; Target version {}".format(
                source.dxfversion, target.dxfversion))

    def is_compatible(self):
        if self.source.dxfversion == self.target.dxfversion:
            return True
        # The basic DXF structure has been changed with version AC1012 (AutoCAD R13)
        # It is not possible to copy from R12 to a newer version and
        # it is not possible to copy from R13 or newer versions to R12.
        if self.source.dxfversion == 'AC1009' or self.target.dxfversion == 'AC1009':
            return False
        # It is always possible to copy from older to newer versions (except R12).
        if self.target.dxfversion > self.source.dxfversion:
            return True
        # It is possible to copy from newer to older versions, if the entity is defined for both versions.
        # But this can not be granted by default. You can operate with that by __init__(s, t, strict_mode=False).
        return False

    def import_entities(self, query="*"):
        modelspace = self.target.modelspace()
        new_handle = self.target._handles.next
        for entity in modelspace:  # entity is GraphicEntity() or inherited
            handle = new_handle()
            entity.dxf.handle = handle  # new handle is always required
            self.target.entitydb[handle] = entity.tags  # add tag list to entity database
            modelspace.add_entity(entity)  # add entity to modelspace

    def import_blocks(self, query="*", conflict="discard"):
        """ Import block definitions.

        :param str query: name of blocks to import, "*" for all
        :param str conflict: discard|replace|rename
        """
        raise NotImplementedError()

    def import_tables(self, query="*", conflict="discard"):
        """ Import table entries.

        :param str conflict: discard|replace
        """
        raise NotImplementedError()