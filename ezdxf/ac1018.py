#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2004/AC1018
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .ac1018hdrvars import VARMAP
from .ac1015 import AC1015Engine

class AC1018Engine(AC1015Engine):
    HEADERVARS = dict(VARMAP)

