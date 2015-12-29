# Purpose: AC1009 creation interface
# Created: 10.03.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..lldxf import const


class GraphicsFactory(object):
    """ Abstract base class for Layout()
    """
    def __init__(self, dxffactory):
        self._dxffactory = dxffactory

    def build_and_add_entity(self, type_, dxfattribs):
        raise NotImplementedError("Abstract method call.")

    def add_point(self, location, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['location'] = location
        return self.build_and_add_entity('POINT', dxfattribs)

    def add_line(self, start, end, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['end'] = end
        return self.build_and_add_entity('LINE', dxfattribs)

    def add_circle(self, center, radius, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        return self.build_and_add_entity('CIRCLE', dxfattribs)

    def add_arc(self, center, radius, start_angle, end_angle, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        dxfattribs['start_angle'] = start_angle
        dxfattribs['end_angle'] = end_angle
        return self.build_and_add_entity('ARC', dxfattribs)

    def add_solid(self, points, dxfattribs=None):
        return self._add_quadrilateral('SOLID', points, dxfattribs)

    def add_trace(self, points, dxfattribs=None):
        return self._add_quadrilateral('TRACE', points, dxfattribs)

    def add_3Dface(self, points, dxfattribs=None):
        return self._add_quadrilateral('3DFACE', points, dxfattribs)

    def add_text(self, text, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['text'] = text
        dxfattribs.setdefault('insert', (0, 0))
        return self.build_and_add_entity('TEXT', dxfattribs)

    def add_blockref(self, name, insert, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        blockref = self.build_and_add_entity('INSERT', dxfattribs)
        return blockref

    def add_auto_blockref(self, name, insert, values, dxfattribs=None):
        def get_dxfattribs(attdef):
            dxfattribs = attdef.clone_dxf_attribs()
            dxfattribs.pop('prompt', None)
            dxfattribs.pop('handle', None)
            return dxfattribs

        def unpack(dxfattribs):
            tag = dxfattribs.pop('tag')
            text = values.get(tag, "")
            insert = dxfattribs.pop('insert')
            return tag, text, insert

        def autofill(blockref, blockdef):
            # ATTRIBs are placed relative to the base point
            for attdef in blockdef.attdefs():
                dxfattribs = get_dxfattribs(attdef)
                tag, text, insert = unpack(dxfattribs)
                blockref.add_attrib(tag, text, insert, dxfattribs)

        if dxfattribs is None:
            dxfattribs = {}
        autoblock = self._dxffactory.blocks.new_anonymous_block()
        blockref = autoblock.add_blockref(name, (0, 0))
        blockdef = self._dxffactory.blocks[name]
        autofill(blockref, blockdef)
        return self.add_blockref(autoblock.name, insert, dxfattribs)

    def add_attrib(self, tag, text, insert=(0, 0), dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        return self.build_and_add_entity('ATTRIB', dxfattribs)

    def add_polyline2d(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        closed = dxfattribs.pop('closed', False)
        polyline = self.build_and_add_entity('POLYLINE', dxfattribs)
        polyline.close(closed)
        polyline.append_vertices(points)
        return polyline

    def add_polyline3d(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYLINE
        return self.add_polyline2d(points, dxfattribs)

    def add_polymesh(self, size=(3, 3), dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYMESH
        m_size = max(size[0], 2)
        n_size = max(size[1], 2)
        dxfattribs['m_count'] = m_size
        dxfattribs['n_count'] = n_size
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        polymesh = self.build_and_add_entity('POLYLINE', dxfattribs)

        points = [(0, 0, 0)] * (m_size * n_size)
        polymesh.append_vertices(points)  # init mesh vertices
        polymesh.close(m_close, n_close)
        return polymesh.cast()

    def add_polyface(self, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_POLYFACE
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        polyface = self.build_and_add_entity('POLYLINE', dxfattribs)
        polyface.close(m_close, n_close)
        return polyface.cast()

    def _add_quadrilateral(self, type_, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        entity = self.build_and_add_entity(type_, dxfattribs)
        for x, point in enumerate(self._four_points(points)):
            entity[x] = point
        return entity

    @staticmethod
    def _four_points(points):
        if len(points) not in (3, 4):
            raise ValueError('3 or 4 points required.')
        for point in points:
            yield point
        if len(points) == 3:
            yield point  # again

    def add_shape(self, name, insert=(0, 0), size=1.0, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        dxfattribs['size'] = size
        return self.build_and_add_entity('SHAPE', dxfattribs)

    def add_viewport(self, center, size, view_center_point, view_height, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        width, height = size
        attribs = {
            'center': center,
            'width': width,
            'height': height,
            'status': 1,  # by default highest priority (stack order)
            'layer': 'VIEWPORTS',  # use separated layer to turn off for plotting
        }
        attribs.update(dxfattribs)
        # DXF R12 (AC1009): view_center_point and view_height (as many other viewport attributes) are not usual
        # DXF attributes, they are stored as extended DXF tags.
        viewport = self.build_and_add_entity('VIEWPORT', attribs)
        viewport.dxf.id = viewport.get_next_viewport_id()
        with viewport.edit_data() as vp_data:
            vp_data.view_center_point = view_center_point
            vp_data.view_height = view_height
        return viewport
