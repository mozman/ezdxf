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
            self.lasttag = tagcast( (code, value) )
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
    release = 'R12'
    encoding = 'cp1252'
    tag = (999999, '')
    tagreader = TagIterator(stream)
    while tag != (0, 'ENDSEC'):
        tag = next(tagreader)
        if tag.code != 9:
            continue
        if tag.value == '$DWGCODEPAGE':
            encoding = toencoding(next(tagreader).value)
        elif tag.value == '$ACADVER':
            release = acadrelease.get(next(tagreader).value, 'R12')

    return DXFInfo(release, encoding)

class TagCaster:
    def __init__(self):
        self._cast = self._build()

    def _build(self):
        table = {}
        for caster, codes in TYPES:
            for code in codes:
                table[code] = caster
        return table

    def cast(self, tag):
        typecaster = self._cast.get(tag[0], str)
        return DXFTag(tag[0], typecaster(tag[1]))

TYPES = [
    (str, range(0, 10)),
    (float, range(10, 60)),
    (int, range(60, 100)),
    (str, range(100, 106)),
    (float, range(110, 150)),
    (int, range(170, 180)),
    (float, range(210, 240)),
    (int, range(270, 290)),
    (int, range(290, 300)), # bool 1=True 0=False
    (str, range(300, 370)),
    (int, range(370, 390)),
    (str, range(390, 400)),
    (int, range(400, 410)),
    (str, range(410, 420)),
    (int, range(420, 430)),
    (str, range(430, 440)),
    (int, range(440, 460)),
    (float, range(460, 470)),
    (str, range(470, 480)),
    (str, range(480, 482)),
    (str, range(999, 1010)),
    (float, range(1010, 1060)),
    (int, range(1060, 1072)),
]

_TagCaster = TagCaster()
tagcast = _TagCaster.cast
