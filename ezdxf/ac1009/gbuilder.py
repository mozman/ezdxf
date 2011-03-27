#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 graphic builder
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

class AC1009GraphicBuilder:
    def add_line(self, start, end, attribs={}):
        def update_attribs():
            self._set_paper_space(attribs)
            attribs['start'] = start
            attribs['end'] = end

        update_attribs()
        entity = self._build_entity('LINE', attribs)
        self._add_entity(entity)
        return entity

    def _build_entity(self, type_, attribs):
        pass # abstract method

    def _add_entity(self, entity):
        pass # abstract method

    def _set_paper_space(self, attribs):
        pass # abstract method
