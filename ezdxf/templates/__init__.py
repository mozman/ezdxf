# Purpose: DXF drawing templates
# Created: 16.07.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

import os
import io


class TemplateLoader(object):
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
            template_dir = os.path.dirname(__file__)
        return template_dir

    def filepath(self, dxfversion):
        return os.path.join(self._template_dir, self.filename(dxfversion))

    def filename(self, dxfversion):
        return "%s.dxf" % dxfversion

    def getstream(self, dxfversion):
        return io.open(self.filepath(dxfversion), encoding='cp1252')
