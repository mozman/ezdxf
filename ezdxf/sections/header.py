# Purpose: manage header section
# Created: 12.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Tuple, KeysView, Any, Iterator

from collections import OrderedDict

from ezdxf.lldxf.types import strtag
from ezdxf.lldxf.tags import group_tags, Tags, DXFTag
from ezdxf.lldxf.const import DXFStructureError, DXFValueError, DXFKeyError, DXF12, LATEST_DXF_VERSION
from ezdxf.lldxf.validator import header_validator
from ezdxf.sections.headervars import HEADER_VAR_MAP
import logging

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter

MIN_HEADER_TEXT = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
$HANDSEED
  5
FF
"""


class CustomVars:
    """
    Custom Properties are stored as string tuples ('CustomTag', 'CustomValue') in a list object.

    Multiple occurrence of the same 'CustomTag' is allowed, but not well supported by the interface.
    """

    def __init__(self):
        self.properties = list()  # type: List[Tuple[str, str]]

    def __len__(self) -> int:
        return len(self.properties)

    def __iter__(self) -> Iterable[Tuple[str, str]]:
        return iter(self.properties)

    def clear(self) -> None:
        """ Remove all custom properties.
        """
        self.properties.clear()

    def append(self, tag: str, value: str) -> None:
        # custom properties always stored as strings
        self.properties.append((tag, str(value)))

    def get(self, tag: str, default: str = None):
        """ Get value of first occurrence of 'tag'.
        """
        for key, value in self.properties:
            if key == tag:
                return value
        else:
            return default

    def has_tag(self, tag: str) -> bool:
        return self.get(tag) is not None

    def remove(self, tag: str, all: bool = False) -> None:
        """ Remove first occurrence of 'tag', removes all occurrences if param all is True.
        """
        found_tag = False
        for item in self.properties:
            if item[0] == tag:
                self.properties.remove(item)
                found_tag = True
                if not all:
                    return
        if not found_tag:
            raise DXFValueError("Tag '%s' does not exist" % tag)

    def replace(self, tag: str, value: str) -> None:
        """ Replaces the value of the first custom property `tag` by a new `value`.
        """
        properties = self.properties
        for index in range(len(properties)):
            name = properties[index][0]
            if name == tag:
                properties[index] = (name, value)
                return

        raise DXFValueError("Tag '%s' does not exist" % tag)

    def write(self, tagwriter: 'TagWriter') -> None:
        for tag, value in self.properties:
            s = "  9\n$CUSTOMPROPERTYTAG\n  1\n{0}\n  9\n$CUSTOMPROPERTY\n  1\n{1}\n".format(tag, value)
            tagwriter.write_str(s)


def default_vars() -> OrderedDict:
    vars = OrderedDict()
    for vardef in HEADER_VAR_MAP.values():
        vars[vardef.name] = HeaderVar(DXFTag(vardef.code, vardef.default))
    return vars


class HeaderSection:
    MIN_HEADER_TAGS = Tags.from_text(MIN_HEADER_TEXT)
    name = 'HEADER'

    def __init__(self):
        self.hdrvars = OrderedDict()
        self.custom_vars = CustomVars()

    @classmethod
    def load(cls, tags: Iterator[DXFTag] = None) -> 'HeaderSection':
        """
        Constructor to generate header variables loaded from DXF files (untrusted environment)

        Args:
            tags: DXF tags as Tags() or ExtendedTags()

        """
        if tags is None:
            tags = cls.MIN_HEADER_TAGS
        section = cls()
        section.load_tags(iter(tags))
        return section

    @classmethod
    def new(cls, dxfversion=LATEST_DXF_VERSION)->'HeaderSection':
        section = HeaderSection()
        section.hdrvars = default_vars()
        section['$ACADVER'] = dxfversion
        return section

    def load_tags(self, tags: Iterator[DXFTag]) -> None:
        """
        Constructor to generate header variables loaded from DXF files (untrusted environment)

        Args:
            tags: DXF tags as Tags() or ExtendedTags()

        """
        tags = tags or self.MIN_HEADER_TAGS
        section_tag = next(tags)
        name_tag = next(tags)

        if section_tag != (0, 'SECTION') or name_tag != (2, 'HEADER'):
            raise DXFStructureError("Critical structure error in HEADER section.")

        groups = group_tags(header_validator(tags), splitcode=9)
        custom_property_stack = []  # collect $CUSTOMPROPERTY/TAG
        for group in groups:
            name = group[0].value
            value = group[1]
            if name in ('$CUSTOMPROPERTYTAG', '$CUSTOMPROPERTY'):
                custom_property_stack.append(value.value)
            else:
                self.hdrvars[name] = HeaderVar(value)

        custom_property_stack.reverse()
        while len(custom_property_stack):
            try:
                self.custom_vars.append(tag=custom_property_stack.pop(), value=custom_property_stack.pop())
            except IndexError:  # internal exception
                break

    @classmethod
    def from_text(cls, text: str) -> 'HeaderSection':
        """ Load constructor from text for testing """
        return cls.load(Tags.from_text(text))

    def _headervar_factory(self, key: str, value: Any) -> DXFTag:
        if key in HEADER_VAR_MAP:
            factory = HEADER_VAR_MAP[key].factory
            return factory(value)
        else:
            raise DXFKeyError('Invalid header variable {}.'.format(key))

    def __len__(self) -> int:
        return len(self.hdrvars)

    def __contains__(self, key) -> bool:
        return key in self.hdrvars

    def varnames(self) -> KeysView:
        return self.hdrvars.keys()

    def write(self, tagwriter: 'TagWriter') -> None:
        def _write(name: str, value: Any) -> None:
            tagwriter.write_tag2(9, name)
            tagwriter.write_str(str(value))

        if self.get('$ACADVER', DXF12) == DXF12 and self.get('$HANDLING', 1) == 0:
            write_handles = False
        else:
            write_handles = True

        tagwriter.write_str("  0\nSECTION\n  2\nHEADER\n")
        # for name, value in self.hdrvars.items():
        for name, value in header_vars_by_priority(self.hdrvars, tagwriter.dxfversion):
            if not write_handles and name == '$HANDSEED':
                continue  # skip $HANDSEED
            _write(name, value)
            if name == "$LASTSAVEDBY":  # ugly hack, but necessary for AutoCAD
                self.custom_vars.write(tagwriter)
        tagwriter.write_str("  0\nENDSEC\n")

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        def _write(name: str, value: Any) -> None:
            tagwriter.write_tag2(9, name)
            tagwriter.write_str(str(value))
        dxfversion = tagwriter.dxfversion
        write_handles = tagwriter.write_handles

        tagwriter.write_str("  0\nSECTION\n  2\nHEADER\n")
        save = self['$ACADVER']
        self['$ACADVER'] = dxfversion
        for name, value in header_vars_by_priority(self.hdrvars, dxfversion):
            if not write_handles and name == '$HANDSEED':
                continue  # skip $HANDSEED
            _write(name, value)
            if name == "$LASTSAVEDBY":  # ugly hack, but necessary for AutoCAD
                self.custom_vars.write(tagwriter)
        self['$ACADVER'] = save
        tagwriter.write_str("  0\nENDSEC\n")

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.hdrvars:
            return self.__getitem__(key)
        else:
            return default

    def __getitem__(self, key: str) -> Any:
        try:
            return self.hdrvars[key].value
        except KeyError:  # map exception
            raise DXFKeyError(str(key))

    def __setitem__(self, key: str, value: Any) -> None:
        try:
            tags = self._headervar_factory(key, value)
        except (IndexError, ValueError):
            raise DXFValueError(str(value))
        self.hdrvars[key] = HeaderVar(tags)

    def __delitem__(self, key: str) -> None:
        try:
            del self.hdrvars[key]
        except KeyError:  # map exception
            raise DXFKeyError(str(key))


def header_vars_by_priority(header_vars: OrderedDict, dxfversion: str) -> Tuple:
    order = []
    for name, value in header_vars.items():
        vardef = HEADER_VAR_MAP.get(name, None)
        if vardef is None:
            logger.info('Header variable {} ignored, dxfversion={}.'.format(name, dxfversion))
            continue
        if vardef.mindxf <= dxfversion <= vardef.maxdxf:
            order.append((vardef.priority, (name, value)))
    order.sort()
    for priority, tag in order:
        yield tag


class HeaderVar:
    def __init__(self, tag: DXFTag):
        self.tag = tag

    @property
    def code(self) -> int:
        return self.tag[0]

    @property
    def value(self) -> Any:
        return self.tag[1]

    @property
    def ispoint(self) -> bool:
        return self.code == 10

    def __str__(self) -> str:
        if self.ispoint:
            code, value = self.tag
            s = []
            for coord in value:
                s.append(strtag((code, coord)))
                code += 10
            return "".join(s)
        else:
            return strtag(self.tag)
