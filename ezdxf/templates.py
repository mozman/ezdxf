#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: template file management
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

import os

class TemplateFinder:
    def __init__(self, template_dir=None):
        self._template_dir = self._get_template_dir(template_dir)

    @property
    def template_dir(self):
        return self._template_dir

    @template_dir.setter
    def template_dir(self, template_dir):
        self._template_dir = self._get_template_dir(template_dir)

    def _get_template_dir(self, template_dir):
        if template_dir is None:
            mydir = os.path.dirname(__file__)
            template_dir = os.path.join(mydir, 'templates')
        return template_dir

    def template_filepath(self, dxfversion):
        return os.path.join(self._template_dir, self.template_filename(dxfversion))

    def template_filename(self, dxfversion):
        return "%s.dxf" % dxfversion
