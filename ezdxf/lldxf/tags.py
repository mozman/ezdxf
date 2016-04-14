# Purpose: tag reader
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .const import acad_release, DXFStructureError
from .types import NONE_TAG, strtag2, DXFTag, is_point_code, cast_tag
from ..tools.codepage import toencoding
from ..tools.compressedstring import CompressedString
from .tagger import string_tagger, skip_comments, stream_tagger

COMMENT_CODE = 999


def write_tags(stream, tags):
    for tag in tags:
        if isinstance(tag, CompressedTags):
            tag.write(stream)
        else:
            stream.write(strtag2(tag))


def text2tags(text):
    return Tags.from_text(text)


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
        self.release = acad_release.get(value, 'R12')

    def HANDSEED(self, value):
        self.handseed = value


def dxf_info(stream):
    info = DXFInfo()
    tag = (999999, '')
    tagreader = stream_tagger(stream)
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


class Tags(list):
    """ DXFTag() chunk as flat list. """
    def write(self, stream):
        write_tags(stream, self)

    @classmethod
    def from_text(cls, text):
        return cls(skip_comments(string_tagger(text)))

    def __copy__(self):
        return self.__class__(DXFTag(*tag) for tag in self)

    clone = __copy__

    def get_handle(self):
        """Get DXF handle. Raises ValueError if handle not exists.

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
        """Replace existing handle.
        """
        for index, tag in enumerate(self):
            if tag.code in (5, 105):
                self[index] = DXFTag(tag.code, new_handle)
                return

    def dxftype(self):
        return self[0].value

    def has_tag(self, code):
        return any(True for tag in self if tag.code == code)

    def find_first(self, code, default=ValueError):
        """Returns value of first DXFTag(code, value) or default if default != ValueError, else raises ValueError.
        """
        for tag in self:
            if tag.code == code:
                return tag.value
        if default is ValueError:
            raise ValueError(code)
        else:
            return default

    def get_first_tag(self, code, default=ValueError):
        """Returns first DXFTag(code, value) or default if default != ValueError, else raises ValueError.
        """
        for tag in self:
            if tag.code == code:
                return tag
        if default is ValueError:
            raise ValueError(code)
        else:
            return default

    def find_all(self, code):
        """Returns a list of DXFTag(code, value).
        """
        return [tag for tag in self if tag.code == code]

    def tag_index(self, code, start=0, end=None):
        """Return first index of DXFTag(code, value).
        """
        if end is None:
            end = len(self)
        index = start
        while index < end:
            if self[index].code == code:
                return index
            index += 1
        raise ValueError(code)

    def update(self, code, value):
        """Update first existing tag, raises ValueError if tag not exists.
        """
        index = self.tag_index(code)
        self[index] = DXFTag(code, value)

    def set_first(self, code, value):
        """Update first existing DXFTag(code, value) or append a new
        DXFTag(code, value).

        """
        try:
            self.update(code, value)
        except ValueError:
            self.append(DXFTag(code, value))

    def remove_tags(self, codes):
        self[:] = [tag for tag in self if tag.code not in set(codes)]

    def collect_consecutive_tags(self, codes, start=0, end=None):
        """Collect all consecutive tags with code in codes, start and end delimits the search range. A tag code not
        in codes ends the process.

        Returns the collected tags in a collection of type Tag().
        """
        codes = frozenset(codes)
        collected_tags = Tags()
        if end is None:
            end = len(self)
        index = start
        while index < end:
            tag = self[index]
            if tag.code in codes:
                collected_tags.append(tag)
                index += 1
            else:
                break
        return collected_tags


class TagGroups(list):
    """Group of tags starts with a SplitTag and ends before the next SplitTag. A SplitTag is a tag with
    code == splitcode, like (0, 'SECTION') for splitcode == 0.
    """
    def __init__(self, tags, splitcode=0):
        super(TagGroups, self).__init__()
        self.splitcode = splitcode
        self._build_groups(tags, splitcode)

    def _build_groups(self, tags, splitcode):
        def append(tag):  # first do nothing, skip tags in front of the first split tag
            pass
        group = None
        for tag in tags:  # has to work with iterators/generators
            if tag.code == splitcode:
                if group is not None:
                    self.append(group)
                group = Tags([tag])
                append = group.append  # redefine append: add tags to this group
            else:
                append(tag)
        if group is not None:
            self.append(group)

    def get_name(self, index):
        return self[index][0].value

    @classmethod
    def from_text(cls, text, splitcode=0):
        return cls(Tags.from_text(text), splitcode)


def strip_tags(tags, codes):
    return Tags((tag for tag in tags if tag.code not in codes))


class CompressedTags(object):
    """Store multiple tags, compressed by zlib, as one DXFTag(code, value). value is a CompressedString() object.
    """
    def __init__(self, code, tags):
        self.code = code
        self.value = CompressedString("".join(strtag2(tag) for tag in tags))

    def __getitem__(self, item):
        if item == 0:
            return self.code
        elif item == 1:
            return self.value
        else:
            raise IndexError

    def decompress(self):
        return Tags.from_text(self.value.decompress())

    def write(self, stream):
        stream.write(self.value.decompress())
