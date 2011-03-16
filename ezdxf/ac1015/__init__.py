#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf factory for R2000/AC1015
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .headervars import VARMAP
from ..ac1009 import AC1009Factory

class AC1015Factory(AC1009Factory):
    HEADERVARS = dict(VARMAP)
