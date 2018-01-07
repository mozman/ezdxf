# Purpose: tag reader
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .const import acad_release, DXFStructureError, DXFValueError, DXFIndexError
from .types import NONE_TAG, strtag2, DXFTag, is_point_code, cast_tag
from ..tools.codepage import toencoding
from ..tools.compressedstring import CompressedString
from .tagger import string_tagger, skip_comments, low_level_tagger

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
    tagreader = low_level_tagger(stream)
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
    """
    DXFTag() chunk as flat list.
    """
    def write(self, stream):
        write_tags(stream, self)

    @classmethod
    def from_text(cls, text):
        return cls(skip_comments(string_tagger(text)))

    def __copy__(self):
        return self.__class__(DXFTag(*tag) for tag in self)

    clone = __copy__

    def get_handle(self):
        """
        Get DXF handle. Raises ValueError if handle not exists.

        Returns:
            handle as hex-string like 'FF'
        """
        handle = ''
        for tag in self:
            if tag.code in (5, 105):
                handle = tag.value
                break
        try:
            int(handle, 16)  # check for valid handle
        except ValueError:
            raise DXFValueError('Invalid handle value "{}".'.format(handle))
        return handle

    def replace_handle(self, new_handle):
        """
        Replace existing handle.

        Args:
            new_handle: new handle as hex string
        """
        for index, tag in enumerate(self):
            if tag.code in (5, 105):
                self[index] = DXFTag(tag.code, new_handle)
                return

    def dxftype(self):
        return self[0].value

    def has_tag(self, code):
        """
        Returns True if a DXFTag() with group code == code is present else False.

        Args:
            code: group code as int
        """
        return any(True for tag in self if tag.code == code)

    def get_first_value(self, code, default=DXFValueError):
        """
        Returns value of first DXFTag(code, value) or default if default != DXFValueError, else raises DXFValueError.

        Args:
            code: group code as int
            default: return value for default case or raises DXFValueError
        """
        for tag in self:
            if tag.code == code:
                return tag.value
        if default is DXFValueError:
            raise DXFValueError(code)
        else:
            return default

    def get_first_tag(self, code, default=DXFValueError):
        """
        Returns first DXFTag(code, value) or default if default != ValueError, else raises DXFValueError.

        Args:
            code: group code as int
            default: return value for default case or raises DXFValueError
        """
        for tag in self:
            if tag.code == code:
                return tag
        if default is DXFValueError:
            raise DXFValueError(code)
        else:
            return default

    def find_all(self, code):
        """
        Returns a list of DXFTag(code, value).

        Args:
            code: group code as int
        """
        return [tag for tag in self if tag.code == code]

    def tag_index(self, code, start=0, end=None):
        """
        Return first index of DXFTag(code, value).

        Args:
            code: group code as int
            start: start index as int
            end: end index as int, if None end index = len(self)
        """
        if end is None:
            end = len(self)
        index = start
        while index < end:
            if self[index].code == code:
                return index
            index += 1
        raise DXFValueError(code)

    def update(self, code, value):
        """
        Update first existing tag, raises DXFValueError if tag not exists.

        Args:
            code: group code as int
            value: tag value
        """
        index = self.tag_index(code)
        self[index] = DXFTag(code, value)

    def set_first(self, code, value):
        """
        Update first existing DXFTag(code, value) or append a new  DXFTag(code, value).

        Args:
            code: group code as int
            value: tag value
        """
        try:
            self.update(code, value)
        except DXFValueError:
            self.append(DXFTag(code, value))

    def remove_tags(self, codes):
        """
        Remove tags inplace with group codes specified in codes.

        Args:
            codes: iterable of group codes

        Returns:
            Tags() object
        """
        self[:] = [tag for tag in self if tag.code not in frozenset(codes)]

    def collect_consecutive_tags(self, codes, start=0, end=None):
        """
        Collect all consecutive tags with code in codes, start and end delimits the search range. A tag code not
        in codes ends the process.

        Args:
            codes: iterable of group codes
            start: start index as int
            end: end index as int, if None end index = len(self)

        Returns:
            collected tags as Tags().
        """
        codes = frozenset(codes)
        index = int(start)
        if end is None:
            end = len(self)
        bag = self.__class__()

        while index < end:
            tag = self[index]
            if tag.code in codes:
                bag.append(tag)
                index += 1
            else:
                break
        return bag

    @classmethod
    def strip(cls, tags, codes):
        """
        Strips all tags with group codes in codes from tags.

        Args:
            tags: iterable of DXFTags() objects
            codes: iterable of group codes
        """
        return cls((tag for tag in tags if tag.code not in frozenset(codes)))


class TagGroups(list):
    """
    Group of tags starts with a SplitTag and ends before the next SplitTag. A SplitTag is a tag with code == splitcode,
    like (0, 'SECTION') for splitcode == 0.
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


class CompressedTags(object):
    """
    Store multiple tags, compressed by zlib, as one DXFTag(code, value). value is a CompressedString() object.
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
            raise DXFIndexError

    def decompress(self):
        return Tags.from_text(self.value.decompress())

    def write(self, stream):
        stream.write(self.value.decompress())
