#!/usr/bin/env python
#coding:utf-8
# Purpose: AC1009 graphic builder
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .. import const


class BuilderConnector(object):
    """ Link between GraphicBuilder and Layout/BlockLayout.

    requires: IBuilderConnector
    ---------------------------
    def _set_paperspace(entity)
    def _get_entity_by_handle(handle) -- set connection to Layout or BlockLayout
    self._entityspace (a list of handles)
    self._dxffactory

    """
    def _build_entity(self, type_, dxfattribs):
        entity = self._dxffactory.create_db_entry(type_, dxfattribs)
        self._set_paperspace(entity)
        return entity

    def _get_entity_at_index(self, index):
        return self._get_entity_by_handle(self._entityspace[index])

    def _append_entity(self, entity):
        self._entityspace.append(entity.dxf.handle)

    def _get_index(self, entity):
        return self._entityspace.index(entity.dxf.handle)

    def _insert_entities(self, index, entities):
        handles = [entity.dxf.handle for entity in entities]
        self._entityspace[index:index] = handles

    def _remove_entities(self, index, count=1):
        self._entityspace[index:index+count] = []


class AC1009GraphicBuilder(BuilderConnector):
    """ A mixin for: Layout, BlockLayout.

    required interface: IGraphicBuilder
    -----------------------------------
    def _build_entity(type_, dxfattribs)
    def _append_entity(entity)
    def _get_index(entity)
    def _get_entity_at_index(index)
    def _insert_entities(index, entities)
    def _remove_entities(index, count=1)

    """
    def add_line(self, start, end, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['end'] = end
        return self._create('LINE', dxfattribs)

    def add_circle(self, center, radius, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        return self._create('CIRCLE', dxfattribs)

    def add_arc(self, center, radius, startangle, endangle, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        dxfattribs['startangle'] = startangle
        dxfattribs['endangle'] = endangle
        return self._create('ARC', dxfattribs)

    def add_solid(self, points, dxfattribs=None):
        return self._add_quadrilateral('SOLID', points, dxfattribs)

    def add_trace(self, points, dxfattribs=None):
        return self._add_quadrilateral('TRACE', points, dxfattribs)

    def add_3Dface(self, points, dxfattribs=None):
        return self._add_quadrilateral('3DFACE', points, dxfattribs)

    def add_text(self, text, style='STANDARD', dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['text'] = text
        dxfattribs['style'] = style
        return self._create('TEXT', dxfattribs)

    def add_blockref(self, name, insert, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        blockref = self._create('INSERT', dxfattribs)
        blockref.set_builder(self)
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
            return (tag, text, insert)

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
        return self._create('ATTRIB', dxfattribs)

    def add_polyline2d(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        closed = dxfattribs.pop('closed', False)
        polyline = self._create('POLYLINE', dxfattribs)
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
        return self._create('VERTEX', dxfattribs)

    def add_seqend(self):
        return self._create('SEQEND', {})

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
        polymesh = self._create('POLYLINE', dxfattribs)
        vtxflags = { 'flags': polymesh.get_vertex_flags() }
        append_null_points(msize * nsize, vtxflags)
        self.add_seqend()
        polymesh.close(mclose, nclose)
        return polymesh.cast()

    def add_polyface(self, dxfattribs={}):
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_POLYFACE
        mclose = dxfattribs.pop('mclose', False)
        nclose = dxfattribs.pop('nclose', False)
        polyface = self._create('POLYLINE', dxfattribs)
        self.add_seqend()
        polyface.close(mclose, nclose)
        return polyface.cast()

    def _add_quadrilateral(self, type_, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        entity = self._create(type_, dxfattribs)
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

    def _create(self, type_, dxfattribs):
        entity = self._build_entity(type_, dxfattribs)
        self._append_entity(entity)
        entity.set_builder(self)
        return entity
