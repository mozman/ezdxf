#!/usr/bin/env python3
# encoding: utf-8
# Purpose: Python 2/3 compatibility layer
# Created: 12.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License

import sys

PY3 = sys.version_info.major > 2

if PY3:
    basestring = str
    ustr = str
    from collections.abc import Sequence
else:
    from collections import Sequence
    ustr = unicode

def isstring(s):
    return isinstance(s, basestring)