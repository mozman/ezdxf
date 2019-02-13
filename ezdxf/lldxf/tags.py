# Created: 10.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from copy import deepcopy
from typing import Iterable, List, TextIO, Any, TYPE_CHECKING

from .const import acad_release, DXFStructureError, DXFValueError, DXFIndexError, HEADER_VAR_MARKER, STRUCTURE_MARKER
from .types import NONE_TAG, DXFTag, is_point_code, EMBEDDED_OBJ_MARKER, EMBEDDED_OBJ_STR
from .tagger import internal_tag_compiler, low_level_tagger

from ezdxf.tools.codepage import toencoding

if TYPE_CHECKING:
    from ezdxf.eztypes import TagValue

COMMENT_CODE = 999


class DXFInfo(object):
    def __init__(self):
        self.release = 'R12'
        self.version = 'AC1009'
        self.encoding = 'cp1252'
        self.handseed = '0'

    def set_header_var(self, name: str, value: str) -> int:
        if name == '$ACADVER':
            self.version = value
            self.release = acad_release.get(value, 'R12')
        elif name == '$DWGCODEPAGE':
            self.encoding = toencoding(value)
        elif name == '$HANDSEED':
            self.handseed = value
        else:
            return 0
        return 1


def dxf_info(stream: TextIO) -> DXFInfo:
    info = DXFInfo()
    tagger = low_level_tagger(stream)  # filters already comments
    if next(tagger) != (0, 'SECTION'):  # maybe a DXF structure error, handled by later processing
        return info
    if next(tagger) != (2, 'HEADER'):  # no leading HEADER section like DXF R12 with only ENTITIES section
        return info
    tag = NONE_TAG
    found = 0
    while tag != (0, 'ENDSEC'):  # until end of HEADER section
        tag = next(tagger)
        if tag.code != HEADER_VAR_MARKER:
            continue
        name = tag.value
        value = next(tagger).value
        found += info.set_header_var(name, value)
        if found > 2:  # all expected values collected
            break
    return info


class Tags(list):
    """
    DXFTag() chunk as flat list.

    """

    @classmethod
    def from_text(cls, text: str) -> 'Tags':
        return cls(internal_tag_compiler(text))

    def __copy__(self) -> 'Tags':
        return self.__class__(tag.clone() for tag in self)

    clone = __copy__

    def get_handle(self) -> str:
        """
        Get DXF handle. Raises DXFValueError if handle not exists.

        Returns: handle as hex-string like 'FF'

        """
        try:
            code, handle = self[1]  # fast path  for most common cases
        except IndexError:
            raise DXFValueError('No handle found.')

        if code == 5 or code == 105:
            return handle

        for code, handle in self:
            if code in (5, 105):
                return handle
        raise DXFValueError('No handle found.')

    def replace_handle(self, new_handle: str) -> None:
        """
        Replace existing handle.

        Args:
            new_handle: new handle as hex string

        """
        for index, tag in enumerate(self):
            if tag.code in (5, 105):
                self[index] = DXFTag(tag.code, new_handle)
                return

    def dxftype(self) -> str:
        return self[0].value

    def has_tag(self, code: int) -> bool:
        """
        Returns True if a DXF tag with group code == code is present else False.

        Args:
            code: group code as int

        """
        return any(True for tag in self if tag.code == code)

    def get_first_value(self, code: int, default=DXFValueError) -> 'TagValue':
        """
        Returns value of first DXF tag with given group code or default if default != DXFValueError, else raises DXFValueError.

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

    def get_first_tag(self, code: int, default=DXFValueError) -> DXFTag:
        """
        Returns first DXF tag with given group code or default if default != DXFValueError, else raises DXFValueError.

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

    def find_all(self, code: int) -> List[DXFTag]:
        """
        Returns a list of DXF tag with given group code.

        Args:
            code: group code as int

        """
        return [tag for tag in self if tag.code == code]

    def tag_index(self, code: int, start: int = 0, end: int = None) -> int:
        """
        Return index of first DXF tag with given group code.

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

    def update(self, tag: DXFTag) -> None:
        """
        Update first existing tag with same group code as tag, raises DXFValueError if tag not exists.

        """
        index = self.tag_index(tag.code)
        self[index] = tag

    def set_first(self, tag: DXFTag) -> None:
        """
        Update first existing tag with group code tag.code or append tag.

        """
        try:
            self.update(tag)
        except DXFValueError:
            self.append(tag)

    def remove_tags(self, codes: Iterable[int]) -> None:
        """
        Remove all tags inplace with group codes specified in codes.

        Args:
            codes: iterable of group codes

        Returns: Tags() object

        """
        self[:] = [tag for tag in self if tag.code not in frozenset(codes)]

    def remove_tags_except(self, codes: Iterable[int]) -> None:
        """
        Remove all tags inplace except those with group codes specified in codes.

        Args:
            codes: iterable of group codes

        """
        self[:] = [tag for tag in self if tag.code in frozenset(codes)]

    def collect_consecutive_tags(self, codes: Iterable[int], start: int = 0, end: int = None) -> 'Tags':
        """
        Collect all consecutive tags with group code in codes, start and end delimits the search range. A tag code not
        in codes ends the process.

        Args:
            codes: iterable of group codes
            start: start index as int
            end: end index as int, if None end index = len(self)

        Returns: collected tags as Tags() object

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

    def has_embedded_objects(self) -> bool:
        for tag in self:
            if tag.code == EMBEDDED_OBJ_MARKER and tag.value == EMBEDDED_OBJ_STR:
                return True
        return False

    @classmethod
    def strip(cls, tags: 'Tags', codes: Iterable[int]) -> 'Tags':
        """
        Strips all tags with group codes in codes from tags.

        Args:
            tags: iterable of DXFTags() objects
            codes: iterable of group codes

        """
        return cls((tag for tag in tags if tag.code not in frozenset(codes)))


def text2tags(text: str) -> Tags:
    return Tags.from_text(text)


def group_tags(tags: Iterable[DXFTag], splitcode: int = STRUCTURE_MARKER) -> Iterable[Tags]:
    """
    Group of tags starts with a SplitTag and ends before the next SplitTag.
    A SplitTag is a tag with code == splitcode, like (0, 'SECTION') for splitcode == 0.

    Args:
        tags: iterable of DXFTag()
        splitcode int: group code of split tag

    Yields: list of DXFTag()

    """

    def append(tag):  # first do nothing, skip tags in front of the first split tag
        pass

    group = None
    for tag in tags:  # has to work with iterators/generators
        if tag.code == splitcode:
            if group is not None:
                yield group
            group = Tags([tag])
            append = group.append  # redefine append: add tags to this group
        else:
            append(tag)
    if group is not None:
        yield group


def text_to_multi_tags(text: str, code: int = 303, size: int = 255, line_ending: str = '^J') -> List[DXFTag]:
    text = ''.join(text).replace('\n', line_ending)

    def chop():
        start = 0
        end = size
        while start < len(text):
            yield text[start:end]
            start = end
            end += size

    return [DXFTag(code, part) for part in chop()]


def multi_tags_to_text(tags, line_ending: str = '^J') -> str:
    return ''.join(tag.value for tag in tags).replace(line_ending, '\n')
