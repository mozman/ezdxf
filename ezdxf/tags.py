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
        def undo_tag():
            self.undo = False
            self.lineno += 2
            return self.lasttag

        def next_tag():
            try:
                code = int(self.readline())
                value = self.readline().rstrip('\n')
            except:
                raise StopIteration()
            self.lasttag = tagcast( (code, value) )
            return self.lasttag

        if self.undo:
            return undo_tag()
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

def text2tags(text):
    return Tags(StringIterator(text))

class DXFInfo:
    def __init__(self):
        self.release = 'R12'
        self.version = 'AC1009'
        self.encoding = 'cp1252'
        self.handseed = 0

    def DWGCODEPAGE(self, value):
        self.encoding = toencoding(value)

    def ACADVER(self, value):
        self.version = value
        self.release = acadrelease.get(value, 'R12')

    def HANDSEED(self, value):
        self.handseed = int(value, 16)


def dxfinfo(stream):
    info = DXFInfo()
    tag = (999999, '')
    tagreader = TagIterator(stream)
    while tag != (0, 'ENDSEC'):
        tag = next(tagreader)
        if tag.code != 9:
            continue
        name = tag.value[1:]
        method = getattr(info, name, None)
        if method is not None:
            method(next(tagreader).value)
    return info

TAG_STRING_FORMAT = '%3d\n%s\n'
def strtag(tag):
    return TAG_STRING_FORMAT % tag

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

class Tags(list):
    def write(self, stream):
        for tag in self:
            stream.write(strtag(tag))

    def gethandle(self, handles):
        handle = None
        try:
            index = self.findfirst(5)
            return self[index].value
        except ValueError:
            pass
        try:
            index = self.findfirst(105)
            return self[index].value
        except ValueError:
            return handles.next

    def findall(self, code):
        return [ tag for tag in self if tag.code == code ]

    def findfirst(self, code):
        return self.findnext(code, 0)

    def findnext(self, code, start=0):
        for index in range(start, len(self)):
            if self[index].code == code:
                return index
        raise ValueError(code)

    def settag(self, code, value):
        for index, tag in enumerate(self):
            if tag.code == code:
                self[index] = DXFTag(code, value)
                return

    @staticmethod
    def fromtext(text):
        return Tags(StringIterator(text))
