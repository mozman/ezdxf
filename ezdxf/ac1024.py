#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2010/AC1024
# Created: 12.03.2011
# Copyright (C), Manfred Moitzi
# License: GPLv3

from .ac1024hdrvars import VARMAP
from .ac1021 import AC1021Engine

class AC1024Engine(AC1021Engine):
    HEADERVARS = dict(VARMAP)