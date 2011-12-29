#!/usr/bin/env python
#coding:utf-8
# Purpose: template file management
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import os

from .tags import dxfinfo

class TemplateFinder:
    def __init__(self, template_dir=None):
        self._template_dir = self._get_template_dir(template_dir)

    @property
    def templatedir(self):
        return self._template_dir

    @templatedir.setter
    def templatedir(self, template_dir):
        self._template_dir = self._get_template_dir(template_dir)

    def _get_template_dir(self, template_dir):
        if template_dir is None:
            mydir = os.path.dirname(__file__)
            template_dir = os.path.join(mydir, 'templates')
        return template_dir

    def filepath(self, dxfversion):
        return os.path.join(self._template_dir, self.filename(dxfversion))

    def filename(self, dxfversion):
        return "%s.dxf" % dxfversion

    def getstream(self, dxfversion):
        filename = self.filepath(dxfversion)
        return open(self.filepath(dxfversion), encoding='cp1252')

