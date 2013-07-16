# Purpose: AC1009 creation interface
# Created: 10.03.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .. import const


class GraphicsFactory(object):
    """ Abstract base class for Layout()
    """
    def __init__(self, dxffactory):
        self._dxffactory = dxffactory

    def build_and_add_entity(self, type_, dxfattribs):
        raise NotImplementedError("Abstract method call.")

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

    def add_arc(self, center, radius, startangle, endangle, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        dxfattribs['startangle'] = startangle
        dxfattribs['endangle'] = endangle
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
        blockref.set_layout(self)
        return blockref

    def add_autoblockref(self, name, insert, values, dxfattribs=None):
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

    def add_attrib(self, tag, text, insert, dxfattribs=None):
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
        dxfattribs = {'flags': polyline.get_vertex_flags()}
        for point in points:
            self.add_vertex(point, dxfattribs)
        self.add_seqend()
        return polyline

    def add_polyline3d(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYLINE
        polyline = self.add_polyline2d(points, dxfattribs)
        return polyline

    def add_vertex(self, location, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['location'] = location
        return self.build_and_add_entity('VERTEX', dxfattribs)

    def add_seqend(self):
        return self.build_and_add_entity('SEQEND', {})

    def add_polymesh(self, size=(3, 3), dxfattribs=None):
        def append_null_points(count, vtxflags):
            for x in range(count):
                self.add_vertex((0, 0, 0), vtxflags)

        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYMESH
        msize = max(size[0], 2)
        nsize = max(size[1], 2)
        dxfattribs['mcount'] = msize
        dxfattribs['ncount'] = nsize
        mclose = dxfattribs.pop('mclose', False)
        nclose = dxfattribs.pop('nclose', False)
        polymesh = self.build_and_add_entity('POLYLINE', dxfattribs)
        vtxflags = { 'flags': polymesh.get_vertex_flags() }
        append_null_points(msize * nsize, vtxflags)
        self.add_seqend()
        polymesh.close(mclose, nclose)
        return polymesh.cast()

    def add_polyface(self, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_POLYFACE
        mclose = dxfattribs.pop('mclose', False)
        nclose = dxfattribs.pop('nclose', False)
        polyface = self.build_and_add_entity('POLYLINE', dxfattribs)
        self.add_seqend()
        polyface.close(mclose, nclose)
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
