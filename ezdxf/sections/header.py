# Purpose: manage header section
# Created: 12.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Tuple, KeysView, Any, Iterator, Union, Sequence

from collections import OrderedDict

from ezdxf.lldxf.types import strtag
from ezdxf.lldxf.tags import group_tags, Tags, DXFTag
from ezdxf.lldxf.const import DXFStructureError, DXFValueError, DXFKeyError, DXF12, LATEST_DXF_VERSION, DXF2018
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
    Stores custom properties in the DXF header as $CUSTOMPROPERTYTAG and $CUSTOMPROPERTY values. Custom properties are
    just supported by DXF R2004 (AC1018) or later. `ezdxf` can create custom properties at older DXF versions,
    but AutoCAD will not show this properties.
    """

    def __init__(self):
        self.properties = list()  # type: List[Tuple[str, str]]

    def __len__(self) -> int:
        """ Count of custom properties. """
        return len(self.properties)

    def __iter__(self) -> Iterable[Tuple[str, str]]:
        """ Iterate over all custom properties as ``(tag, value)`` tuples. """
        return iter(self.properties)

    def clear(self) -> None:
        """ Remove all custom properties. """
        self.properties.clear()

    def append(self, tag: str, value: str) -> None:
        """ Add custom property as ``(tag, value)`` tuple. """
        # custom properties always stored as strings
        self.properties.append((tag, str(value)))

    def get(self, tag: str, default: str = None):
        """ Returns the value of the first custom property `tag`. """
        for key, value in self.properties:
            if key == tag:
                return value
        else:
            return default

    def has_tag(self, tag: str) -> bool:
        """ Returns ``True`` if custom property `tag` exist. """
        return self.get(tag) is not None

    def remove(self, tag: str, all: bool = False) -> None:
        """ Removes the first occurrence of custom property `tag`, removes all occurrences if `all` is ``True``.
        Raises `:class:`DXFValueError` if `tag`  does not exist.
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
        Raises :class:`DXFValueError` if `tag`  does not exist.
        """
        properties = self.properties
        for index in range(len(properties)):
            name = properties[index][0]
            if name == tag:
                properties[index] = (name, value)
                return

        raise DXFValueError("Tag '%s' does not exist" % tag)

    def write(self, tagwriter: 'TagWriter') -> None:
        """ Export custom properties as DXF tags. (internal API) """
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

        (internal API)
        """
        if tags is None:  # create default header
            return cls.new(dxfversion=DXF12)  # file without header are by default DXF R12
        section = cls()
        section.load_tags(iter(tags))
        return section

    @classmethod
    def new(cls, dxfversion=LATEST_DXF_VERSION) -> 'HeaderSection':
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
        """ Returns count of header variables. """
        return len(self.hdrvars)

    def __contains__(self, key) -> bool:
        """ Returns ``True`` if header variable `key` exist. """
        return key in self.hdrvars

    def varnames(self) -> KeysView:
        """ Returns an iterable of all header variable names. """
        return self.hdrvars.keys()

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        """ Exports header section as DXF tags. (internal API) """
        def _write(name: str, value: Any) -> None:
            if value.value is None:
                logger.info('did not write header var {}, value is None.'.format(name))
                return
            tagwriter.write_tag2(9, name)
            vardef = HEADER_VAR_MAP[name]

            # group code for header var $ACADMAINTVER changed from 70 to 90 in DXF version R2018.
            if name == '$ACADMAINTVER':
                vardef.code = 70 if dxfversion < DXF2018 else 90

            # fix invalid group codes
            if vardef.code != value.code:
                value = HeaderVar((vardef.code, value.value))
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
            if name == '$LASTSAVEDBY':  # ugly hack, but necessary for AutoCAD
                self.custom_vars.write(tagwriter)
        self['$ACADVER'] = save
        tagwriter.write_str("  0\nENDSEC\n")

    def get(self, key: str, default: Any = None) -> Any:
        """ Returns value of header variable `key` if exist, else the `default` value. """
        if key in self.hdrvars:
            return self.__getitem__(key)
        else:
            return default

    def __getitem__(self, key: str) -> Any:
        """ Get header variable `key` by index operator like: :code:`drawing.header['$ACADVER']` """
        try:
            return self.hdrvars[key].value
        except KeyError:  # map exception
            raise DXFKeyError(str(key))

    def __setitem__(self, key: str, value: Any) -> None:
        """ Set header variable `key` to `value` by index operator like: :code:`drawing.header['$ANGDIR'] = 1`"""
        try:
            tags = self._headervar_factory(key, value)
        except (IndexError, ValueError):
            raise DXFValueError(str(value))
        self.hdrvars[key] = HeaderVar(tags)

    def __delitem__(self, key: str) -> None:
        """ Delete header variable `key` by index operator like: :code:`del drawing.header['$ANGDIR']` """
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
    def __init__(self, tag: Union[DXFTag, Sequence]):
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
