# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

from ezdxf.lldxf.const import DXFValueError, DXFKeyError

from .graphics import GraphicEntity, ExtendedTags, make_attribs, DXFAttr

_INSERT_TPL = """0
INSERT
5
0
8
0
2
BLOCKNAME
10
0.0
20
0.0
30
0.0
41
1.0
42
1.0
43
1.0
50
0.0
"""
# IMPORTANT: Bug in AutoCAD 2010
# attribsfollow = 0, for NO attribsfollow, does not work with ACAD 2010
# if no attribs attached to the INSERT entity, omit attribsfollow tag


class Insert(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_INSERT_TPL)
    DXFATTRIBS = make_attribs({
        'attribs_follow': DXFAttr(66, default=0),
        'name': DXFAttr(2),
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'xscale': DXFAttr(41, default=1.0),
        'yscale': DXFAttr(42, default=1.0),
        'zscale': DXFAttr(43, default=1.0),
        'rotation': DXFAttr(50, default=0.0),
        'column_count': DXFAttr(70, default=1),
        'row_count': DXFAttr(71, default=1),
        'column_spacing': DXFAttr(44, default=0.0),
        'row_spacing': DXFAttr(45, default=0.0),
    })

    def attribs(self):
        """
        Iterate over all appended ATTRIB entities, yields Attrib() objects.

        """
        if self.dxf.attribs_follow == 0:
            return
        dxffactory = self.dxffactory
        handle = self.tags.link
        while handle is not None:
            entity = dxffactory.wrap_handle(handle)
            next_entity = entity.tags.link
            if next_entity is None:  # found SeqEnd
                return
            else:
                yield entity
                handle = next_entity

    def place(self, insert=None, scale=None, rotation=None):
        """
        Set placing attributes of the INSERT entity.

        Args:
            insert: insert position as (x, y [,z]) tuple
            scale: (scale_x, scale_y, scale_z) tuple
            rotation (float): rotation angle in degrees

        Returns:
            Insert() object (fluent interface)

        """
        if insert is not None:
            self.dxf.insert = insert
        if scale is not None:
            if len(scale) != 3:
                raise DXFValueError("Parameter scale has to be a 3-tuple.")
            x, y, z = scale
            self.dxf.xscale = x
            self.dxf.yscale = y
            self.dxf.zscale = z
        if rotation is not None:
            self.dxf.rotation = rotation
        return self

    def grid(self, size=(1, 1), spacing=(1, 1)):
        """
        Set grid placing attributes of the INSERT entity.

        Args:
            size: grid size as (row_count, column_count) tuple
            spacing: distance between placing as (row_spacing, column_spacing) tuple

        Returns:
            Insert() object (fluent interface)

        """
        if len(size) != 2:
            raise DXFValueError("Parameter size has to be a (row_count, column_count)-tuple.")
        if len(spacing) != 2:
            raise DXFValueError("Parameter spacing has to be a (row_spacing, column_spacing)-tuple.")
        self.dxf.row_count = size[0]
        self.dxf.column_count = size[1]
        self.dxf.row_spacing = spacing[0]
        self.dxf.column_spacing = spacing[1]
        return self

    def get_attrib(self, tag, search_const=False):
        """
        Get attached ATTRIB entity by *tag*.

        Args:
            tag (str): tag name
            search_const (bool): search also const ATTDEF entities

        Returns:
            Attrib()/Attdef() object

        """
        for attrib in self.attribs():
            if tag == attrib.dxf.tag:
                return attrib
        if search_const and self.drawing is not None:
            block = self.drawing.blocks[self.dxf.name]  # raises KeyError() if not found
            for attdef in block.get_const_attdefs():
                if tag == attdef.dxf.tag:
                    return attdef
        return None

    def get_attrib_text(self, tag, default=None, search_const=False):
        """
        Get content text of attached ATTRIB entity *tag*.

        Args:
            tag (str): tag name
            default (str): default value if tag is absent
            search_const (bool): search also const ATTDEF entities

        Returns:
            content text as str

        """
        attrib = self.get_attrib(tag, search_const)
        if attrib is None:
            return default
        return attrib.dxf.text

    def has_attrib(self, tag, search_const=False):
        """
        Check if ATTRIB for *tag* exists.

        Args:
            tag (str): tag name
            search_const: search also const ATTDEF entities

        """
        return self.get_attrib(tag, search_const) is not None

    def add_attrib(self, tag, text, insert=(0, 0), dxfattribs=None):
        """
        Add new ATTRIB entity.

        Args:
            tag (str): tag name
            text (str): content text
            insert: insert position as tuple (x, y[, z])
            dxfattribs: additional DXF attributes

        Returns:
            Attrib() object

        """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib_entity = self._new_entity('ATTRIB', dxfattribs)
        self._append_attrib_entity(attrib_entity)
        return attrib_entity

    def _append_attrib_entity(self, entity):
        has_no_attribs_attached = self.tags.link is None
        if has_no_attribs_attached or self.dxf.attribs_follow == 0:
            prev = self
            seqend = self._new_entity('SEQEND', {})
        else:
            attribs = list(self.attribs())
            prev = attribs[-1]
            seqend = self.dxffactory.wrap_handle(prev.tags.link)

        prev.tags.link = entity.dxf.handle
        entity.tags.link = seqend.dxf.handle
        self.dxf.attribs_follow = 1

    def delete_attrib(self, tag, ignore=False):
        """
        Delete attached ATTRIB entity `tag`, raises a KeyError exception if `tag` does not exist, set `ignore` to True,
        to ignore not existing ATTRIB entities.
        
        Args:
            tag (str): ATTRIB name 
            ignore (bool): False -> raise KeyError exception if `tag` does not exist 

        """
        if self.dxf.attribs_follow == 0:
            if ignore:
                return
            else:
                raise DXFKeyError(tag)

        dxffactory = self.dxffactory
        handle = self.tags.link
        prev = self
        while handle is not None:
            entity = dxffactory.wrap_handle(handle)
            next_entity = entity.tags.link
            if next_entity is None:  # found SeqEnd
                break
            else:
                if entity.dxf.tag == tag:
                    prev.tags.link = next_entity  # remove entity from linked list
                    self.entitydb.delete_entity(entity)
                    self._fix_attribs()
                    return
                prev = entity
                handle = next_entity
        if not ignore:
            raise DXFKeyError(tag)

    def delete_all_attribs(self):
        """
        Delete all ATTRIB entities attached to the INSERT entity and the following SEQEND entity. Ignores the value
        of dxf.attribs_follow.
         
        """
        db = self.entitydb
        handle = self.tags.link
        while handle is not None:
            entity_tags = db[handle]
            db.delete_handle(handle)
            handle = entity_tags.link
            entity_tags.link = None

        self.tags.link = None
        self.dxf.attribs_follow = 0

    def _fix_attribs(self):
        if self.dxf.attribs_follow == 0:
            self.delete_all_attribs()
        else:
            handle = self.tags.link
            if handle is None:
                self.dxf.attribs.follow = 0
                return
            entity = self.dxffactory.wrap_handle(handle)
            if entity.dxftype() == 'SEQEND':
                # last attrib was deleted, only the SEQEND entity remains
                self.entitydb.delete_entity(entity)
                self.dxf.attribs_follow = 0
                self.tags.link = None
                return

    def destroy(self):
        """
        Delete all attached ATTRIB entities from entity database.

        Caution: this method is meant for internal usage.

        """
        self.delete_all_attribs()
