# Purpose: dxf engine for R2010/AC1024
# Created: 20.05.2013
# Copyright (C), Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .headervars import VARMAP
from ..ac1024 import AC1024Factory


class AC1027Factory(AC1024Factory):
    HEADERVARS = dict(VARMAP)