# Purpose: DXF drawing templates
# Created: 16.07.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from typing import TextIO
import os


class TemplateLoader:
    def __init__(self, template_dir: str = None):
        self._template_dir = self._get_template_dir(template_dir)

    @property
    def templatedir(self) -> str:
        return self._template_dir

    @templatedir.setter
    def templatedir(self, template_dir: str) -> None:
        self._template_dir = self._get_template_dir(template_dir)

    def _get_template_dir(self, template_dir: str) -> str:
        if template_dir is None:
            template_dir = os.path.dirname(__file__)
        return template_dir

    def filepath(self, dxfversion: str) -> str:
        return os.path.join(self._template_dir, self.filename(dxfversion))

    def filename(self, dxfversion: str) -> str:
        return "%s.dxf" % dxfversion

    def getstream(self, dxfversion: str) -> TextIO:
        """
        Templates use only ASCII encoded characters, using standard encoding `cp1252` should be safe.

        """
        return open(self.filepath(dxfversion), mode='rt', encoding='cp1252')
