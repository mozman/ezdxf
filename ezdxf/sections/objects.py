# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .classes import ClassesSection


class ObjectsSection(ClassesSection):
    name = 'objects'

    def roothandle(self):
        return self._entity_space[0]

