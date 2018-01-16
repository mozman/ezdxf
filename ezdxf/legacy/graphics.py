# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf import const
from ..lldxf.const import VERTEXNAMES, DXFInternalEzdxfError, DXFValueError, DXFKeyError, DXFIndexError
from ..dxfentity import DXFEntity
from .facemixins import PolyfaceMixin, PolymeshMixin


class QuadrilateralMixin(object):
    def __getitem__(self, num):
        return self.get_dxf_attrib(VERTEXNAMES[num])

    def __setitem__(self, num, value):
        return self.set_dxf_attrib(VERTEXNAMES[num], value)


def make_attribs(additional=None):
    dxfattribs = {
        'handle': DXFAttr(5),
        'layer': DXFAttr(8, default='0'),  # layername as string
        'linetype': DXFAttr(6, default='BYLAYER'),  # linetype as string, special names BYLAYER/BYBLOCK
        'color': DXFAttr(62, default=256),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
        'thickness': DXFAttr(39, default=0),  # thickness of 2D elements
        'paperspace': DXFAttr(67, default=0),  # 0 .. modelspace, 1 .. paperspace
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),  # Z-axis of OCS (Object-Coordinate-System)
    }
    if additional is not None:
        dxfattribs.update(additional)
    return DXFAttributes(DefSubclass(None, dxfattribs))


class GraphicEntity(DXFEntity):
    """ Default graphic entity wrapper, allows access to following dxf attributes:

     - handle
     - layer
     - linetype
     - color
     - paperspace
     - extrusion

     Wrapper for all unsupported graphic entities.
    """
    DXFATTRIBS = make_attribs()


_LINE_TPL = """  0
LINE
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 11
1.0
 21
1.0
 31
1.0
"""


class Line(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_LINE_TPL)
    DXFATTRIBS = make_attribs({
        'start': DXFAttr(10, xtype='Point2D/3D'),
        'end': DXFAttr(11, xtype='Point2D/3D'),
    })


_POINT_TPL = """  0
POINT
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
"""


class Point(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_POINT_TPL)
    DXFATTRIBS = make_attribs({
        'location': DXFAttr(10, xtype='Point2D/3D'),
    })


_CIRCLE_TPL = """  0
CIRCLE
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
"""


class Circle(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_CIRCLE_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype='Point2D/3D'),
        'radius': DXFAttr(40),
    })


_ARC_TPL = """  0
ARC
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
 50
0
 51
360
"""


class Arc(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_ARC_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype='Point2D/3D'),
        'radius': DXFAttr(40),
        'start_angle': DXFAttr(50),
        'end_angle': DXFAttr(51),
    })


_TRACE_TPL = """  0
TRACE
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 11
0.0
 21
0.0
 31
0.0
 12
0.0
 22
0.0
 32
0.0
 13
0.0
 23
0.0
 33
0.0
"""


class Trace(GraphicEntity, QuadrilateralMixin):
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL)
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, xtype='Point2D/3D'),
        'vtx1': DXFAttr(11, xtype='Point2D/3D'),
        'vtx2': DXFAttr(12, xtype='Point2D/3D'),
        'vtx3': DXFAttr(13, xtype='Point2D/3D'),
    })


class Solid(Trace):
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL.replace('TRACE', 'SOLID'))


class Face(Trace):
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL.replace('TRACE', '3DFACE'))
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, xtype='Point3D'),
        'vtx1': DXFAttr(11, xtype='Point3D'),
        'vtx2': DXFAttr(12, xtype='Point3D'),
        'vtx3': DXFAttr(13, xtype='Point3D'),
        'invisible_edge': DXFAttr(70, default=0),
    })


_TEXT_TPL = """  0
TEXT
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  1
TEXTCONTENT
 50
0.0
 51
0.0
  7
STANDARD
 41
1.0
 71
0
 72
0
 73
0
 11
0.0
 21
0.0
 31
0.0
"""


class Text(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_TEXT_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),  # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, default=0.0),  # in degrees, vertical = 0deg
        'style': DXFAttr(7, default='STANDARD'),  # text style
        'width': DXFAttr(41, default=1.0),  # width FACTOR!
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(73,  default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })

    def set_pos(self, p1, p2=None, align=None):
        if align is None:
            align = self.get_align()
        align = align.upper()
        self.set_align(align)
        self.set_dxf_attrib('insert', p1)
        if align in ('ALIGNED', 'FIT'):
            if p2 is None:
                raise DXFValueError("Alignment '{}' requires a second alignment point.".format(align))
        else:
            p2 = p1
        self.set_dxf_attrib('align_point', p2)
        return self

    def get_pos(self):
        p1 = self.dxf.insert
        p2 = self.get_dxf_attrib('align_point', (0., 0., 0.))
        align = self.get_align()
        if align == 'LEFT':
            return align, p1, None
        if align in ('FIT', 'ALIGN'):
            return align, p1, p2
        return align, p2, None

    def set_align(self, align='LEFT'):
        align = align.upper()
        halign, valign = const.TEXT_ALIGN_FLAGS[align]
        self.set_dxf_attrib('halign', halign)
        self.set_dxf_attrib('valign', valign)
        return self

    def get_align(self):
        halign = self.get_dxf_attrib('halign', 0)
        valign = self.get_dxf_attrib('valign', 0)
        if halign > 2:
            valign = 0
        return const.TEXT_ALIGNMENT_BY_FLAGS.get((halign, valign), 'LEFT')


_BLOCK_TPL = """  0
BLOCK
  5
0
  8
0
  2
BLOCKNAME
  3
BLOCKNAME
 70
0
 10
0.0
 20
0.0
 30
0.0
  1

"""


class Block(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_BLOCK_TPL)
    DXFATTRIBS = make_attribs({
        'name': DXFAttr(2),
        'name2': DXFAttr(3),
        'flags': DXFAttr(70),
        'base_point': DXFAttr(10, xtype='Point2D/3D'),
        'xref_path': DXFAttr(1),
    })


class EndBlk(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text("  0\nENDBLK\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {'handle': DXFAttr(5)}))


_INSERT_TPL = """  0
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


class SeqEnd(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text("  0\nSEQEND\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'paperspace': DXFAttr(67, default=0),
    }))


_ATTRIB_TPL = """  0
ATTRIB
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  1
DEFAULTTEXT
  2
TAG
 70
0
 50
0.0
 51
0.0
 41
1.0
  7
STANDARD
 71
0
 72
0
 73
0
 74
0
 11
0.0
 21
0.0
 31
0.0
"""


def _set_flag_state(flags, mask, state):
    if bool(state):
        return flags | mask
    else:
        return flags & ~mask


class Attrib(Text):
    TEMPLATE = ExtendedTags.from_text(_ATTRIB_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'rotation': DXFAttr(50, default=0.0),
        'oblique': DXFAttr(51, default=0.0),
        'width': DXFAttr(41, default=1.0),  # width factor
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(74, default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })

    @property
    def is_const(self):
        """
        This is a constant attribute.
        """
        return bool(self.dxf.flags & const.ATTRIB_CONST)

    @is_const.setter
    def is_const(self, state):
        """
        This is a constant attribute.
        """
        self.dxf.flags = _set_flag_state(self.dxf.flags, const.ATTRIB_CONST, state)

    @property
    def is_invisible(self):
        """
        Attribute is invisible (does not appear).
        """
        return bool(self.dxf.flags & const.ATTRIB_INVISIBLE)

    @is_invisible.setter
    def is_invisible(self, state):
        """
        Attribute is invisible (does not appear).
        """
        self.dxf.flags = _set_flag_state(self.dxf.flags, const.ATTRIB_INVISIBLE, state)

    @property
    def is_verify(self):
        """
        Verification is required on input of this attribute. (CAD application feature)
        """
        return bool(self.dxf.flags & const.ATTRIB_VERIFY)

    @is_verify.setter
    def is_verify(self, state):
        """
        Verification is required on input of this attribute. (CAD application feature)
        """
        self.dxf.flags = _set_flag_state(self.dxf.flags, const.ATTRIB_VERIFY, state)


    @property
    def is_preset(self):
        """
        No prompt during insertion. (CAD application feature)
        """
        return bool(self.dxf.flags & const.ATTRIB_IS_PRESET)

    @is_preset.setter
    def is_preset(self, state):
        """
        No prompt during insertion. (CAD application feature)
        """
        self.dxf.flags = _set_flag_state(self.dxf.flags, const.ATTRIB_IS_PRESET, state)


_ATTDEF_TPL = """  0
ATTDEF
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  1
DEFAULTTEXT
  3
PROMPTTEXT
  2
TAG
 70
0
 50
0.0
 51
0.0
 41
1.0
  7
STANDARD
 71
0
 72
0
 73
0
 74
0
 11
0.0
 21
0.0
 31
0.0
"""


class Attdef(Attrib):
    TEMPLATE = ExtendedTags.from_text(_ATTDEF_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'prompt': DXFAttr(3),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'rotation': DXFAttr(50, default=0.0),
        'oblique': DXFAttr(51, default=0.0),
        'width': DXFAttr(41, default=1.0),  # width factor
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(74, default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })


_POLYLINE_TPL = """  0
POLYLINE
  5
0
  8
0
 66
1
 70
0
 10
0.0
 20
0.0
 30
0.0
"""


class Polyline(GraphicEntity):
    ANY3D = const.POLYLINE_3D_POLYLINE + const.POLYLINE_3D_POLYMESH + const.POLYLINE_POLYFACE
    TEMPLATE = ExtendedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = make_attribs({
        'elevation': DXFAttr(10, xtype='Point2D/3D'),
        'flags': DXFAttr(70, default=0),
        'default_start_width': DXFAttr(40, default=0.0),
        'default_end_width': DXFAttr(41, default=0.0),
        'm_count': DXFAttr(71, default=0),
        'n_count': DXFAttr(72, default=0),
        'm_smooth_density': DXFAttr(73, default=0),
        'n_smooth_density': DXFAttr(74, default=0),
        'smooth_type': DXFAttr(75, default=0),
    })

    def post_new_hook(self):
        seqend = self._new_entity('SEQEND', {})
        self.tags.link = seqend.dxf.handle

    def set_dxf_attrib(self,  key, value):
        super(Polyline, self).set_dxf_attrib(key, value)
        if key == 'layer':  # if layer of POLYLINE changed, also change layer of VERTEX entities
            self._set_vertices_layer(value)

    def _set_vertices_layer(self, layer_name):
        for vertex in self.vertices():
            vertex.dxf.layer = layer_name

    def get_vertex_flags(self):
        return const.VERTEX_FLAGS[self.get_mode()]

    def get_mode(self):
        if self.is_3d_polyline:
            return 'AcDb3dPolyline'
        elif self.is_polygon_mesh:
            return 'AcDbPolygonMesh'
        elif self.is_poly_face_mesh:
            return 'AcDbPolyFaceMesh'
        else:
            return 'AcDb2dPolyline'

    @property
    def is_2d_polyline(self):
        return self.dxf.flags & Polyline.ANY3D == 0

    @property
    def is_3d_polyline(self):
        return bool(self.dxf.flags & const.POLYLINE_3D_POLYLINE)

    @property
    def is_polygon_mesh(self):
        return bool(self.dxf.flags & const.POLYLINE_3D_POLYMESH)

    @property
    def is_poly_face_mesh(self):
        return bool(self.dxf.flags & const.POLYLINE_POLYFACE)

    @property
    def is_closed(self):
        return bool(self.dxf.flags & const.POLYLINE_CLOSED)

    @property
    def is_m_closed(self):
        return bool(self.dxf.flags & const.POLYLINE_MESH_CLOSED_M_DIRECTION)

    @property
    def is_n_closed(self):
        return bool(self.dxf.flags & const.POLYLINE_MESH_CLOSED_N_DIRECTION)

    def m_close(self):
        self.dxf.flags = self.dxf.flags | const.POLYLINE_MESH_CLOSED_M_DIRECTION

    def n_close(self):
        self.dxf.flags = self.dxf.flags | const.POLYLINE_MESH_CLOSED_N_DIRECTION

    def close(self, m_close, n_close=False):
        if m_close:
            self.m_close()
        if n_close:
            self.n_close()

    def __len__(self):
        count = 0
        db = self.entitydb
        tags = db[self.tags.link]
        while tags.link is not None:
            count += 1
            tags = db[tags.link]
        return count

    def __getitem__(self, pos):
        count = 0
        db = self.entitydb
        tags = db[self.tags.link]
        while tags.link is not None:
            if count == pos:
                return self.dxffactory.wrap_entity(tags)
            count += 1
            tags = db[tags.link]
        raise DXFIndexError("vertex index out of range")

    def vertices(self):
        wrapper = self.dxffactory.wrap_handle
        handle = self.tags.link
        while handle is not None:
            entity = wrapper(handle)
            handle = entity.tags.link
            if entity.dxftype() == 'VERTEX':
                yield entity

    def points(self):
        return (vertex.dxf.location for vertex in self.vertices())

    def append_vertices(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        if len(points) > 0:
            last_vertex = self._get_last_vertex()
            for new_vertex in self._points_to_dxf_vertices(points, dxfattribs):
                self._insert_after(last_vertex, new_vertex)
                last_vertex = new_vertex

    @staticmethod
    def _insert_after(prev_vertex, new_vertex):
        succ = prev_vertex.tags.link
        prev_vertex.tags.link = new_vertex.dxf.handle
        new_vertex.tags.link = succ

    def _get_last_vertex(self):
        db = self.entitydb
        tags = self.tags
        handle = self.dxf.handle
        while tags.link is not None:  # while not SEQEND
            prev_handle = handle
            handle = tags.link
            tags = db[handle]
        return self.dxffactory.wrap_handle(prev_handle)

    def insert_vertices(self, pos, points, dxfattribs=None):
        """ Insert *points* at position *pos*.

        :param points: list of (x, y, z)-tuples
        :param dxfattribs: dict of DXF attributes
        """
        if dxfattribs is None:
            dxfattribs = {}
        if pos > 0:
            insert_vertex = self.__getitem__(pos - 1)
        else:
            insert_vertex = self
        for new_vertex in self._points_to_dxf_vertices(points, dxfattribs):
            self._insert_after(insert_vertex, new_vertex)
            insert_vertex = new_vertex

    def _append_vertices(self, vertices):
        """ Append DXF Vertex() objects.

        :param vertices: list of DXF Vertex() objects
        """
        last_vertex = self._get_last_vertex()
        for vertex in vertices:
            self._insert_after(last_vertex, vertex)
            last_vertex = vertex

    def _points_to_dxf_vertices(self, points, dxfattribs):
        """ Converts point (x,y, z)-tuples into DXF Vertex() objects.

        :param points: list of (x, y,z)-tuples
        :param dxfattribs: dict of DXF attributes
        """
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | self.get_vertex_flags()
        dxfattribs['layer'] = self.get_dxf_attrib('layer', '0')  # all vertices on the same layer as the POLYLINE entity
        vertices = []
        for point in points:
            dxfattribs['location'] = point
            vertices.append(self._new_entity('VERTEX', dxfattribs))
        return vertices

    def delete_vertices(self, pos, count=1):
        db = self.entitydb
        prev_vertex = self.__getitem__(pos-1).tags if pos > 0 else self.tags
        vertex = db[prev_vertex.link]
        while vertex.dxftype() == 'VERTEX':
            db.delete_handle(prev_vertex.link)  # remove from database
            prev_vertex.link = vertex.link  # remove vertex from list
            count -= 1
            if count == 0:
                return
            vertex = db[prev_vertex.link]
        raise DXFValueError("invalid count")

    def _unlink_all_vertices(self):
        # but don't delete it from database
        last_vertex = self._get_last_vertex()
        self.tags.link = last_vertex.tags.link  # link POLYLINE -> SEQEND

    def cast(self):
        mode = self.get_mode()
        if mode == 'AcDbPolyFaceMesh':
            return Polyface.convert(self)
        elif mode == 'AcDbPolygonMesh':
            return Polymesh.convert(self)
        else:
            return self

    def destroy(self):
        db = self.entitydb
        handle = self.tags.link
        while handle is not None:
            tags = db[handle]
            db.delete_handle(handle)
            handle = tags.link
        self.tags.link = None


class Polyface(Polyline, PolyfaceMixin):
    @staticmethod
    def convert(polyline):
        face = Polyface(polyline.tags, polyline.drawing)
        return face

        
class Polymesh(Polyline, PolymeshMixin):
    @staticmethod
    def convert(polyline):
        mesh = Polymesh(polyline.tags, polyline.drawing)
        return mesh


_VERTEX_TPL = """ 0
VERTEX
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
0.0
 41
0.0
 42
0.0
 70
0
"""


class Vertex(GraphicEntity, QuadrilateralMixin):
    FACE_FLAGS = const.VTX_3D_POLYGON_MESH_VERTEX + const.VTX_3D_POLYFACE_MESH_VERTEX
    VTX3D = const.VTX_3D_POLYLINE_VERTEX + const.VTX_3D_POLYGON_MESH_VERTEX + const.VTX_3D_POLYFACE_MESH_VERTEX
    TEMPLATE = ExtendedTags.from_text(_VERTEX_TPL)
    DXFATTRIBS = make_attribs({
        'location': DXFAttr(10, xtype='Point2D/3D'),
        'start_width': DXFAttr(40, default=0.0),
        'end_width': DXFAttr(41, default=0.0),
        'bulge': DXFAttr(42, default=0),
        'flags': DXFAttr(70, default=0),
        'tangent': DXFAttr(50),
        'vtx0': DXFAttr(71),
        'vtx1': DXFAttr(72),
        'vtx2': DXFAttr(73),
        'vtx3': DXFAttr(74),
    })

    @property
    def is_2d_polyline_vertex(self):
        return self.dxf.flags & Vertex.VTX3D == 0

    @property
    def is_3d_polyline_vertex(self):
        return self.dxf.flags & const.VTX_3D_POLYLINE_VERTEX

    @property
    def is_polygon_mesh_vertex(self):
        return self.dxf.flags & const.VTX_3D_POLYGON_MESH_VERTEX

    @property
    def is_poly_face_mesh_vertex(self):
        return self.dxf.flags & Vertex.FACE_FLAGS == Vertex.FACE_FLAGS

    @property
    def is_face_record(self):
        return (self.dxf.flags & Vertex.FACE_FLAGS) == const.VTX_3D_POLYFACE_MESH_VERTEX


_DIMENSION_TPL = """  0
DIMENSION
  5
0
  2
*BLOCKNAME
  3
DIMSTYLE
 10
0.0
 20
0.0
 30
0.0
 11
0.0
 21
0.0
 31
0.0
 12
0.0
 22
0.0
 32
0.0
 70
0
  1

 13
0.0
 23
0.0
 33
0.0
 14
0.0
 24
0.0
 34
0.0
 15
0.0
 25
0.0
 35
0.0
 16
0.0
 26
0.0
 36
0.0
 40
1.0
 50
0.0
"""


class Dimension(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_DIMENSION_TPL)
    DXFATTRIBS = make_attribs({
        'geometry': DXFAttr(2),  # name of pseudo-Block containing the current dimension  entity geometry
        'dimstyle': DXFAttr(3, default='STANDARD'),  # dimension style name
        # The dimension style is stored in Drawing.sections.tables.dimstyles,
        # shortcut Drawings.dimstyles property
        'defpoint': DXFAttr(10, xtype='Point2D/3D'),  # WCS, definition point for all dimension types
        'text_midpoint': DXFAttr(11, xtype='Point2D/3D'),  # OCS, middle point of dimension text
        'translation_vector': DXFAttr(12, 'Point3D'),  # OCS, dimension block translation vector
        'dimtype': DXFAttr(70),  # Dimension type:
        # Values 0–6 are integer values that represent the dimension type.
        # Values 64 and 128 are bit values, which are added to the integer values
        # 0 = Rotated, horizontal, or vertical;
        # 1 = Aligned
        # 2 = Angular;
        # 3 = Diameter;
        # 4 = Radius
        # 5 = Angular 3 point;
        # 6 = Ordinate
        # 64 = Ordinate type. This is a bit value (bit 7) used only with integer
        # value 6. If set, ordinate is X-type; if not set, ordinate is Y-type
        # 128 = This is a bit value (bit 8) added to the other group 70 values if
        # the dimension text has been positioned at a user-defined location
        # rather than at the default location
        'user_text': DXFAttr(1),  # dimension text explicitly entered by the user.
        # If null or "<>", the dimension measurement is drawn as the text,
        # if " " [one blank space], the text is suppressed.
        # Anything else is drawn as the text.
        'defpoint2': DXFAttr(13, xtype='Point2D/3D'),  # WCS, definition point for linear and angular dimensions
        'defpoint3': DXFAttr(14, xtype='Point2D/3D'),  # WCS, definition point for linear and angular dimensions
        'defpoint4': DXFAttr(15, xtype='Point2D/3D'),  # WCS, definition point for diameter, radius, and angular dimensions
        'defpoint5': DXFAttr(16, xtype='Point2D/3D'),  # OCS, point defining dimension arc for angular dimensions
        'leader_length': DXFAttr(40),  # leader length for radius and diameter dimensions
        'angle': DXFAttr(50),  # angle of rotated, horizontal, or vertical linear dimensions
        'horizontal_direction': DXFAttr(51),
        # In addition, all dimension types have an optional group
        # (code 51) that indicates the horizontal direction for the
        # Dimension entity. This determines the orientation of
        # dimension text and dimension lines for horizontal,
        # vertical, and rotated linear dimensions. The group value
        # is the negative of the Entity Coordinate Systems (ECS)
        # angle of the UCS X axis in effect when the Dimension was
        # drawn. The X axis of the UCS in effect when the Dimension
        # was drawn is always parallel to the XY plane for the
        # Dimension's ECS, and the angle between the UCS X axis and
        # the ECS X axis is a single 2D angle. The value in group 51
        # is the angle from horizontal (the effective X axis) to the
        # ECS X axis. Entity Coordinate Systems (ECS) are described
        # later in this section.
        'oblique_angle': DXFAttr(52),
        # Linear dimension types with an oblique angle have an
        # optional group (code 52).When added to the rotation angle
        # of the linear dimension (group code 50) this gives the
        # angle of the extension lines
        'dim_text_rotation': DXFAttr(53),
        # The optional group code 53  is the rotation angle of the
        # dimension text away from its default orientation (the direction
        # of the dimension line).
    })

    @property
    def dim_type(self):
        return self.dxf.dimtype & 7

    @property
    def dim_type_name(self):
        return const.DimensionTypeNames[self.dim_type]

    def dim_style(self):
        if self.drawing is not None:
            dim_style_name = self.dxf.dimstyle
            # raises ValueError if not exists, but all used dim styles should exists!
            return self.drawing.dimstyles.get(dim_style_name)
        else:
            raise DXFInternalEzdxfError('Dimension.drawing attribute not initialized.')


_SHAPE_TPL = """  0
SHAPE
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  2
NAME
 50
0.0
 41
1.0
 51
0.0
"""


# SHAPE is not tested with real world DXF drawings!
class Shape(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_SHAPE_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'size': DXFAttr(40),
        'name': DXFAttr(2),
        'rotation': DXFAttr(50, default=0.0),
        'xscale': DXFAttr(41, default=1.0),
        'oblique': DXFAttr(51, default=0.0),
    })
