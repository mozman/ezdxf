# Purpose: AC1015 graphic builder
# Created: 10.03.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class ModernGraphicsFactory(object):
    def add_lwpolyline(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self.build_and_add_entity('LWPOLYLINE', dxfattribs)
        lwpolyline.set_points(points)
        lwpolyline.closed = closed
        return lwpolyline

    def add_mtext(self, text, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        mtext = self.build_and_add_entity('MTEXT', dxfattribs)
        mtext.set_text(text)
        return mtext

    def add_ray(self, start, unit_vector, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('RAY', dxfattribs)

    def add_xline(self, start, unit_vector, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('XLINE', dxfattribs)

    def add_spline(self, fit_points=None, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        spline = self.build_and_add_entity('SPLINE', dxfattribs)
        if fit_points is not None:
            spline.set_fit_points(fit_points)
        return spline

    def add_body(self, acis_data=None, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        return self._add_acis_entiy('BODY', acis_data, dxfattribs)

    def add_region(self, acis_data=None, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        return self._add_acis_entiy('REGION', acis_data, dxfattribs)

    def add_3dsolid(self, acis_data=None, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        return self._add_acis_entiy('3DSOLID', acis_data, dxfattribs)

    def _add_acis_entiy(self, name, acis_data, dxfattribs):
        entity = self.build_and_add_entity(name, dxfattribs)
        if acis_data is not None:
            entity.set_acis_data(acis_data)
        return entity

    def add_mesh(self, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        return self.build_and_add_entity('MESH', dxfattribs)

    def add_hatch(self, color=7, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['solid_fill'] = 1
        dxfattribs['color'] = color
        dxfattribs['pattern_name'] = 'SOLID'
        return self.build_and_add_entity('HATCH', dxfattribs)

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
            'view_center_point': view_center_point,
            'view_height': view_height,
        }
        attribs.update(dxfattribs)
        viewport = self.build_and_add_entity('VIEWPORT', attribs)
        viewport.dxf.id = viewport.get_next_viewport_id()
        return viewport
