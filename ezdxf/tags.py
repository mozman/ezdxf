#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: tagreader
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from collections import namedtuple
from io import StringIO

from .codepage import toencoding
from .const import acadrelease

DXFTag = namedtuple('DXFTag', 'code value')
NONETAG = DXFTag(999999, 'NONE')

class TagIterator:
    def __init__(self, textfile):
        self.textfile = textfile
        self.lineno = 0
        self.undo = False
        self.lasttag = NONETAG

    def __iter__(self):
        return self

    def __next__(self):
        def stop_iteration():
            return self.lasttag == (0, 'EOF')

        def undo_tag():
            self.undo = False
            self.lineno += 2
            return self.lasttag

        def next_tag():
            code = int(self.readline())
            value = self.readline().rstrip('\n')
            self.lasttag = DXFTag(code, value)
            return self.lasttag

        if self.undo:
            return undo_tag()
        elif stop_iteration():
            raise StopIteration()
        else:
            return next_tag()

    def readline(self):
        self.lineno += 1
        return self.textfile.readline()

    def undotag(self):
        if not self.undo and self.lineno > 0:
            self.undo = True
            self.lineno -= 2
        else:
            raise(ValueError('No tag to undo'))

class StringIterator(TagIterator):
    def __init__(self, dxfcontent):
        super(StringIterator, self).__init__(StringIO(dxfcontent))

DXFInfo = namedtuple('DXFInfo', 'release encoding')
def dxfinfo(stream):
    def get_release(dxfversion):
        try:
            return acadrelease[dxfversion]
        except KeyError:
            return 'R12'

    release = 'R12'
    encoding = 'cp1252'
    tag = (999999, '')
    tagreader = TagIterator(stream)
    while tag != (0, 'ENDSEC'):
        tag = next(tagreader)
        if tag == (9, '$DWGCODEPAGE'):
            encoding = toencoding(next(tagreader).value)
        elif tag == (9, '$ACADVER'):
            release = get_release(next(tagreader).value)

    return DXFInfo(release, encoding)
