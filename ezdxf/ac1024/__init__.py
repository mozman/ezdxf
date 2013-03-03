#!/usr/bin/env python
#coding:utf-8
# Purpose: dxf engine for R2010/AC1024
# Created: 12.03.2011
# Copyright (C), Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .headervars import VARMAP
from ..ac1021 import AC1021Factory


class AC1024Factory(AC1021Factory):
    HEADERVARS = dict(VARMAP)