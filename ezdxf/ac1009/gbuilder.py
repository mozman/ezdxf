#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 graphic builder
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

class AC1009GraphicBuilder:
    # Used as mixin for layout objects.
    # Required interface of host object:
    # def _build_entity(type_, attribs)
    # def _append_entity(self, entity):
    # def _get_position(self, entity):
    # def _get_entity(self, pos):
    # def _insert_entity(self, pos, entity):
    # def _remove_entity(self, pos or entity):

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

    def add_solid(self, points, attribs):
        return self._add_quadrilateral('SOLID', points, attribs={})

    def add_trace(self, points, attribs):
        return self._add_quadrilateral('TRACE', points, attribs={})

    def add_3Dface(self, points, attribs):
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
        for point in points:
            polyline.add_vertex(point)
        self.add_seqend()
        self._close_polyline(polyline, closed)
        return polyline

    def add_polyline3D(self, points, attribs={}, seqend=True):
        polyline = self.add_polyline2d(points, attribs, seqend)
        polyline.setmode('polyline3d')
        return polyline

    def add_vertex(self, point, attribs={}):
        attribs['location'] = point
        return self._create('VERTEX', attribs)

    def add_seqend(self):
        return self._create('SEQEND', {})

    def add_polymesh(self, size=(10, 10), attribs={}):
        def append_null_points(count):
            for x in range(count):
                self.add_vertex((0, 0, 0))
        msize = max(size[0], 2)
        nsize = max(size[1], 2)
        attribs['mcount'] = msize
        attribs['ncount'] = nsize
        mclose = attribs.pop('mclose', False)
        nclose = attribs.pop('nclose', False)
        polymesh = self._create('POLYLINE', attribs)
        polyline.setbuilder(self)
        polymesh.setmode('polymesh')
        append_null_points(msize * nsize)
        polymesh.close(mclose, nclose)
        return polymesh.cast()

    def add_polyface(self, attribs={}):
        mclose = attribs.pop('mclose', False)
        nclose = attribs.pop('nclose', False)
        polyface = self._create('POLYLINE', attribs)
        polyline.setbuilder(self)
        polyface.setmode('polyface')
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
