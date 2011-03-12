#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2000/AC1015
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .ac1015hdrvars import VARMAP
from .ac1009 import AC1009Engine

class AC1015Engine(AC1009Engine):
    HEADERVARS = dict(VARMAP)
