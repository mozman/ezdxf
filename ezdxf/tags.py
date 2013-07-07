# Purpose: tag reader
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import namedtuple
from io import StringIO

from .codepage import toencoding
from .const import acadrelease
from .c23 import ustr

DXFTag = namedtuple('DXFTag', 'code value')
NONE_TAG = DXFTag(999999, 'NONE')
TAG_STRING_FORMAT = '%3d\n%s\n'


class DXFStructureError(Exception):
    pass


class TagIterator(object):
    def __init__(self, textfile):
        self.textfile = textfile
        self.lineno = 0
        self.undo = False
        self.lasttag = NONE_TAG

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
            except UnicodeDecodeError:
                raise # because UnicodeDecodeError() is a subclass of ValueError()
            except (EOFError, ValueError):
                raise StopIteration()
            self.lasttag = cast_tag((code, value))
            return self.lasttag

        if self.undo:
            return undo_tag()
        else:
            return next_tag()
    # for Python 2.7
    next = __next__

    def readline(self):
        self.lineno += 1
        return self.textfile.readline()

    def undotag(self):
        if not self.undo and self.lineno > 0:
            self.undo = True
            self.lineno -= 2
        else:
            raise ValueError('No tag to undo')


class StringIterator(TagIterator):
    def __init__(self, string):
        super(StringIterator, self).__init__(StringIO(string))


def text2tags(text):
    return Tags(StringIterator(text))


class DXFInfo(object):
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

def dxf_info(stream):
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
            # noinspection PyCallingNonCallable
            method(next(tagreader).value)
    return info

def strtag(tag):
    return TAG_STRING_FORMAT % tag

def _build_type_table(types):
    table = {}
    for caster, codes in types:
        for code in codes:
            table[code] = caster
    return table

TYPE_TABLE = _build_type_table([
    (ustr, range(0, 10)),
    (float, range(10, 60)),
    (int, range(60, 100)),
    (ustr, range(100, 106)),
    (float, range(110, 150)),
    (int, range(160, 170)),
    (int, range(170, 180)),
    (float, range(210, 240)),
    (int, range(270, 290)),
    (int, range(290, 300)),  # bool 1=True 0=False
    (ustr, range(300, 370)),
    (int, range(370, 390)),
    (ustr, range(390, 400)),
    (int, range(400, 410)),
    (ustr, range(410, 420)),
    (int, range(420, 430)),
    (ustr, range(430, 440)),
    (int, range(440, 460)),
    (float, range(460, 470)),
    (ustr, range(470, 480)),
    (ustr, range(480, 482)),
    (ustr, range(999, 1010)),
    (float, range(1010, 1060)),
    (int, range(1060, 1072)),
])


def cast_tag(tag, types=TYPE_TABLE):
    caster = types.get(tag[0], ustr)
    return DXFTag(tag[0], caster(tag[1]))


def cast_tag_value(code, value, types=TYPE_TABLE):
    return types.get(code, ustr)(value)


def tag_type(code):
    try:
        return TYPE_TABLE[code]
    except KeyError:
        raise ValueError("Invalid tag code: {}".format(code))


class Tags(list):
    """ DXFTag() chunk as flat list. """
    def write(self, stream):
        for tag in self:
            stream.write(strtag(tag))

    def get_handle(self):
        """ Search handle of a DXFTag() chunk. Raises ValueError if handle
        not exists.

        :returns: handle as hex-string like 'FF'
        """
        handle = ''
        for tag in self:
            if tag.code in (5, 105):
                handle = tag.value
                break
        int(handle, 16)  # check for valid handle
        return handle

    def replace_handle(self, new_handle):
        """Replace existing handle of a DXFTag() chunk.
        """
        index = 0
        tag_count = len(self)
        while index < tag_count:
            tag = self[index]
            if tag.code in (5, 105):
                self[index] = DXFTag(tag.code, new_handle)
                return
            index += 1

    def dxftype(self):
        return self.__getitem__(0).value

    def find_all(self, code):
        """ Returns a list of DXFTag(code, ...). """
        return [tag for tag in self if tag.code == code]

    def tag_index(self, code, start=0, end=None):
        """ Return first index of DXFTag(code, ...). """
        if end is None:
            end = len(self)
        for index, tag in enumerate(self[start:end]):
            if tag.code == code:
                return start + index
        raise ValueError(code)

    def update(self, code, value):
        """ Update first existing tag, raises ValueError if tag not exists. """
        index = self.tag_index(code)
        self[index] = DXFTag(code, value)

    def set_first(self, code, value):
        """ Update first existing DXFTag(code, ...) or append a new
        DXFTag(code, value).

        """
        try:
            self.update(code, value)
        except ValueError:
            # noinspection PyTypeChecker
            self.append(DXFTag(code, value))

    def get_value(self, code):
        index = self.tag_index(code)
        return self[index].value

    @staticmethod
    def from_text(text):
        return Tags(StringIterator(text))

    def __copy__(self):
        return self.__class__(self[:])

    def clone(self):
        return self.__copy__()

class TagGroups(list):
    """
    Group of tags starts with a SplitTag and ends before the next SplitTag.

    A SplitTag is a tag with code == splitcode, like (0, 'SECTION') for splitcode == 0.

    """
    def __init__(self, tags, splitcode=0):
        super(TagGroups, self).__init__()
        self.splitcode = splitcode
        self._build_groups(tags)

    def _build_groups(self, tags):
        def push_group():
            if len(group) > 0:
                self.append(group)

        def start_tag(itags):
            tag = next(itags)
            while tag.code != self.splitcode:
                tag = next(itags)
            return tag

        tag_iterator = iter(tags)
        group = Tags([start_tag(tag_iterator)])

        for tag in tag_iterator:
            if tag.code == self.splitcode:
                push_group()
                group = Tags([tag])
            else:
                group.append(tag)
        push_group()

    def get_name(self, index):
        return self[index][0].value

    @staticmethod
    def from_text(text, splitcode=0):
        return TagGroups(Tags.from_text(text), splitcode)
