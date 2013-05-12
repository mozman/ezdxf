# Purpose: dxf engine for R2007/AC1021
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .headervars import VARMAP
from ..ac1018 import AC1018Factory


class AC1021Factory(AC1018Factory):
    HEADERVARS = dict(VARMAP)
