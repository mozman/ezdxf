#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf factory for R2004/AC1018
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

# Support for new AC1018 entities planned for the future:
# - no new entities intruduced

from .headervars import VARMAP
from ..ac1015 import AC1015Factory

class AC1018Factory(AC1015Factory):
    HEADERVARS = dict(VARMAP)

