#!/usr/bin/env python
#coding:utf-8
# Purpose: tagreader
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import namedtuple, Counter

from .codepage import toencoding
from .const import acadrelease
from .six import StringIO

DXFTag = namedtuple('DXFTag', 'code value')
NONETAG = DXFTag(999999, 'NONE')

class DXFStructureError(Exception):
    pass

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
        self.handseed = '0'

    def DWGCODEPAGE(self, value):
        self.encoding = toencoding(value)

    def ACADVER(self, value):
        self.version = value
        self.release = acadrelease.get(value, 'R12')

    def HANDSEED(self, value):
        self.handseed = value

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

    def castvalue(self, code, value):
        typecaster = self._cast.get(code, str)
        return typecaster(value)

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
casttagvalue = _TagCaster.castvalue

class Tags(list):
    """ DXFTag() chunk as flat list. """
    def write(self, stream):
        for tag in self:
            stream.write(strtag(tag))

    def gethandle(self):
        """ Search handle of a DXFTag() chunk. Raises ValueError if handle
        not exists.

        :returns: handle as hex-string like 'FF'
        """
        handle = ''
        for tag in self:
            if tag.code in (5, 105):
                handle = tag.value
                break
        int(handle, 16) # check for valid handle
        return handle

    def findall(self, code):
        """ Returns a list of DXFTag(code, ...). """
        return [ tag for tag in self if tag.code == code ]

    def tagindex(self, code, start=0, end=None):
        """ Return first index of DXFTag(code, ...). """
        if end is None:
            end = len(self)
        for index in range(start, end):
            if self[index].code == code:
                return index
        raise ValueError(code)

    def update(self, code, value):
        """ Update first existing tag, raises ValueError if tag not exists. """
        index = self.tagindex(code)
        self[index] = DXFTag(code, value)

    def setfirst(self, code, value):
        """ Update first existing DXFTag(code, ...) or append a new
        DXFTag(code, value).

        """
        try:
            self.update(code, value)
        except ValueError:
            self.append( DXFTag(code, value) )

    def getvalue(self, code):
        index = self.tagindex(code)
        return self[index].value

    def getlastvalue(self, code):
        index = self.lastindex(code)
        return self[index].value

    @staticmethod
    def fromtext(text):
        return Tags(StringIterator(text))

    def get_type(self):
        return self.__getitem__(0).value

class TagGroups(list):
    """
    Group of tags starting with a SplitTag and ending before the next SplitTag.

    A SplitTag is a tag with code == splitcode, like (0, 'SECTION') for splitcode=0.

    """
    def __init__(self, tags, splitcode=0):
        super(TagGroups, self).__init__()
        self.splitcode = splitcode
        self._buildgroups(tags)

    def _buildgroups(self, tags):
        def pushgroup():
            if len(group) > 0:
                self.append(group)

        def starttag(itags):
            tag = next(itags)
            while tag.code != self.splitcode:
                tag = next(itags)
            return tag

        itags = iter(tags)
        group = Tags([starttag(itags)])

        for tag in itags:
            if tag.code == self.splitcode:
                pushgroup()
                group = Tags([tag])
            else:
                group.append(tag)
        pushgroup()

    def getname(self, index):
        return self[index][0].value

    @staticmethod
    def fromtext(text, splitcode=0):
        return TagGroups(Tags.fromtext(text), splitcode)

