#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 graphic builder
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .. import const

class BuilderConnector:
    """ A mixin for classes like: Layout, EntitySection.

    implements: IGraphicBuilder
    ---------------------------

    requires: IBuilderConnector
    ---------------------------
    def _set_paperspace(entity)
    self._entityspace (a list of handles)
    self._dxffactory

    """
    def _build_entity(self, type_, attribs):
        entity = self._dxffactory.create_db_entry(type_, attribs)
        self._set_paperspace(entity)
        return entity

    def _get_entity(self, pos):
        handle = self._entityspace[pos]
        return self._dxffactory.wrap_handle(handle)

    def _append_entity(self, entity):
        self._entityspace.append(entity.handle)

    def _get_position(self, entity):
        return self._entityspace.index(entity.handle)

    def _insert_entities(self, pos, entities):
        handles = [entity.handle for entity in entities]
        self._entityspace[pos:pos] = handles

    def _remove_entities(self, pos, count=1):
        self._entityspace[pos:pos+count] = []

class AC1009GraphicBuilder:
    """ A mixin for classes like Layout, Block.

    required interface: IGraphicBuilder
    -----------------------------------
    def _build_entity(type_, attribs)
    def _append_entity(entity)
    def _get_position(entity)
    def _get_entity(pos)
    def _insert_entities(pos, entities)
    def _remove_entities(pos, count=1)

    """
    def add_line(self, start, end, attribs={}):
        attribs['start'] = start
        attribs['end'] = end
        return self._create('LINE', attribs)

    def add_circle(self, center, radius, attribs={}):
        attribs['center'] = center
        attribs['radius'] = radius
        return self._create('CIRCLE', attribs)

    def add_arc(self, center, radius, startangle, endangle, attribs={}):
        attribs['center'] = center
        attribs['radius'] = radius
        attribs['startangle'] = startangle
        attribs['endangle'] = endangle
        return self._create('ARC', attribs)

    def add_solid(self, points, attribs={}):
        return self._add_quadrilateral('SOLID', points, attribs={})

    def add_trace(self, points, attribs={}):
        return self._add_quadrilateral('TRACE', points, attribs={})

    def add_3Dface(self, points, attribs={}):
        return self._add_quadrilateral('3DFACE', points, attribs={})

    def add_text(self, text, style='STANDARD', attribs={}):
        attribs['text'] = text
        attribs['style'] = style
        return self._create('TEXT', attribs)

    def add_blockref(self, name, insert, attribs={}):
        attribs['name'] = name
        attribs['insert'] = insert
        return self._create('INSERT', attribs)

    def add_polyline2D(self, points, attribs={}):
        closed = attribs.pop('closed', False)
        polyline = self._create('POLYLINE', attribs)
        polyline.setbuilder(self)
        polyline.close(closed)
        attribs = {'flags': polyline.get_vertex_flags()}
        for point in points:
            self.add_vertex(point, attribs)
        self.add_seqend()
        return polyline

    def add_polyline3D(self, points, attribs={}):
        attribs['flags'] = attribs.get('flags', 0) | const.POLYLINE_3D_POLYLINE
        polyline = self.add_polyline2D(points, attribs)
        return polyline

    def add_vertex(self, location, attribs={}):
        attribs['location'] = location
        return self._create('VERTEX', attribs)

    def add_seqend(self):
        return self._create('SEQEND', {})

    def add_polymesh(self, size=(3, 3), attribs={}):
        def append_null_points(count, vtxflags):
            for x in range(count):
                self.add_vertex((0, 0, 0), vtxflags)
        attribs['flags'] = attribs.get('flags', 0) | const.POLYLINE_3D_POLYMESH
        msize = max(size[0], 2)
        nsize = max(size[1], 2)
        attribs['mcount'] = msize
        attribs['ncount'] = nsize
        mclose = attribs.pop('mclose', False)
        nclose = attribs.pop('nclose', False)
        polymesh = self._create('POLYLINE', attribs)
        polymesh.setbuilder(self)
        vtxflags = { 'flags': polymesh.get_vertex_flags() }
        append_null_points(msize * nsize, vtxflags)
        self.add_seqend()
        polymesh.close(mclose, nclose)
        return polymesh.cast()

    def add_polyface(self, attribs={}):
        attribs['flags'] = attribs.get('flags', 0) | const.POLYLINE_POLYFACE
        mclose = attribs.pop('mclose', False)
        nclose = attribs.pop('nclose', False)
        polyface = self._create('POLYLINE', attribs)
        polyface.setbuilder(self)
        self.add_seqend()
        polyface.close(mclose, nclose)
        return polyface.cast()

    def _add_quadrilateral(self, type_, points, attribs={}):
        entity = self._create(type_, attribs)
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
            yield point # again

    def _create(self, type_, attribs):
        entity = self._build_entity(type_, attribs)
        self._append_entity(entity)
        return entity
