# Purpose: AC1009 creation interface
# Created: 10.03.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .lldxf import const


class GraphicsFactory(object):
    """ Abstract base class for BaseLayout()
    """
    def __init__(self, dxffactory):
        self._dxffactory = dxffactory

    @property
    def dxfversion(self):
        return self._dxffactory.dxfversion

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

    def add_3dface(self, points, dxfattribs=None):
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

        def viewport_AC1009():
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

        def viewport_AC1015():
            attribs = {
                'center': center,
                'width': width,
                'height': height,
                'status': 1,  # by default highest priority (stack order)
                'layer': 'VIEWPORTS',  # use separated layer to turn off for plotting
                'view_center_point': view_center_point,
                'view_height': view_height,
            }
            attribs.update(dxfattribs)
            viewport = self.build_and_add_entity('VIEWPORT', attribs)
            viewport.dxf.id = viewport.get_next_viewport_id()
            return viewport

        return viewport_AC1009() if self.dxfversion <= 'AC1009'else viewport_AC1015()

# new entities in DXF AC1015 (R2000)

    def add_lwpolyline(self, points, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('LWPOLYLINE requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self.build_and_add_entity('LWPOLYLINE', dxfattribs)
        lwpolyline.set_points(points)
        lwpolyline.closed = closed
        return lwpolyline

    def add_ellipse(self, center, major_axis=(1, 0, 0), ratio=1, start_param=0, end_param=6.283185307, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('ELLIPSE requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['center'] = center
        dxfattribs['major_axis'] = major_axis
        dxfattribs['ratio'] = ratio
        dxfattribs['start_param'] = start_param
        dxfattribs['end_param'] = end_param
        return self.build_and_add_entity('ELLIPSE', dxfattribs)

    def add_mtext(self, text, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('MTEXT requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        mtext = self.build_and_add_entity('MTEXT', dxfattribs)
        mtext.set_text(text)
        return mtext

    def add_ray(self, start, unit_vector, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('RAY requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('RAY', dxfattribs)

    def add_xline(self, start, unit_vector, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('XLINE requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('XLINE', dxfattribs)

    def add_spline(self, fit_points=None, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('SPLINE requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        spline = self.build_and_add_entity('SPLINE', dxfattribs)
        if fit_points is not None:
            spline.set_fit_points(fit_points)
        return spline

    def add_body(self, acis_data=None, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('BODY requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))

        if dxfattribs is None:
            dxfattribs = {}
        return self._add_acis_entiy('BODY', acis_data, dxfattribs)

    def add_region(self, acis_data=None, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('REGION requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        return self._add_acis_entiy('REGION', acis_data, dxfattribs)

    def add_3dsolid(self, acis_data=None, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('3DSOLID requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        return self._add_acis_entiy('3DSOLID', acis_data, dxfattribs)

    def _add_acis_entiy(self, name, acis_data, dxfattribs):
        entity = self.build_and_add_entity(name, dxfattribs)
        if acis_data is not None:
            entity.set_acis_data(acis_data)
        return entity

    def add_hatch(self, color=7, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('HATCH requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['solid_fill'] = 1
        dxfattribs['color'] = color
        dxfattribs['pattern_name'] = 'SOLID'
        return self.build_and_add_entity('HATCH', dxfattribs)

    def add_mesh(self, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise const.DXFVersionError('MESH requires DXF version AC1015 (R2000) or later, '
                                        'actual DXF version is {}.'.format(self.dxfversion))
        if dxfattribs is None:
            dxfattribs = {}
        return self.build_and_add_entity('MESH', dxfattribs)
