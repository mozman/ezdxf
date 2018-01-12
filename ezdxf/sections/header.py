# Purpose: manage header section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import OrderedDict

from ..tools.c23 import ustr
from ..lldxf.types import strtag
from ..lldxf.tags import group_tags, Tags
from ..lldxf.const import DXFStructureError, DXFValueError, DXFKeyError
from ..lldxf.validator import header_validator


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
  0
ENDSEC
"""


class CustomVars(object):
    """ Custom Properties are stored as string tuples ('CustomTag', 'CustomValue') in a list object.

    Multiple occurrence of the same 'CustomTag' is allowed, but not well supported by the interface.
    """
    def __init__(self):
        self.properties = list()

    def __len__(self):
        return len(self.properties)

    def __iter__(self):
        return iter(self.properties)

    def clear(self):
        """ Remove all custom properties.
        """
        self.properties.clear()

    def append(self, tag, value):
        # custom properties always stored as strings
        self.properties.append((tag, ustr(value)))

    def get(self, tag, default=None):
        """ Get value of first occurrence of 'tag'.
        """
        for key, value in self.properties:
            if key == tag:
                return value
        else:
            return default

    def has_tag(self, tag):
        return self.get(tag) is not None

    def remove(self, tag, all=False):
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

    def replace(self, tag, value):
        """ Replaces the value of the first custom property `tag` by a new `value`.
        """
        properties = self.properties
        for index in range(len(properties)):
            name = properties[index][0]
            if name == tag:
                properties[index] = (name, value)
                return

        raise DXFValueError("Tag '%s' does not exist" % tag)

    def write(self, stream):
        for tag, value in self.properties:
            stream.write("  9\n$CUSTOMPROPERTYTAG\n  1\n%s\n" % tag)
            stream.write("  9\n$CUSTOMPROPERTY\n  1\n%s\n" % value)


class HeaderSection(object):
    MIN_HEADER_TAGS = Tags.from_text(MIN_HEADER_TEXT)
    name = 'header'

    def __init__(self, tags=None):
        if tags is None:
            tags = self.MIN_HEADER_TAGS
        self.hdrvars = OrderedDict()
        self.custom_vars = CustomVars()
        self._build(tags)

    def set_headervar_factory(self, factory):
        self._headervar_factory = factory

    def __len__(self):
        return len(self.hdrvars)

    def __contains__(self, key):
        return key in self.hdrvars

    def _build(self, tags):
        if tags[0] != (0, 'SECTION') or \
           tags[1] != (2, 'HEADER') or \
           tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in HEADER section.")

        if len(tags) == 3:  # DXF file with empty header section
            return
        groups = group_tags(header_validator(tags[2:-1]), splitcode=9)
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

    def varnames(self):
        return self.hdrvars.keys()

    def write(self, stream):
        def _write(name, value):
            stream.write("  9\n%s\n" % name)
            stream.write(ustr(value))

        stream.write("  0\nSECTION\n  2\nHEADER\n")
        for name, value in self.hdrvars.items():
            _write(name, value)
            if name == "$LASTSAVEDBY":  # ugly hack, but necessary for AutoCAD
                self.custom_vars.write(stream)

        stream.write("  0\nENDSEC\n")

    def __getitem__(self, key):
        try:
            return self.hdrvars[key].value
        except KeyError:  # map exception
            raise DXFKeyError(str(key))

    def get(self, key, default=None):
        if key in self.hdrvars:
            return self.__getitem__(key)
        else:
            return default

    def __setitem__(self, key, value):
        try:
            tags = self._headervar_factory(key, value)
        except (IndexError, ValueError):
            raise DXFValueError(str(value))
        self.hdrvars[key] = HeaderVar(tags)

    def __delitem__(self, key):
        try:
            del self.hdrvars[key]
        except KeyError:  # map exception
            raise DXFKeyError(str(key))


class HeaderVar:
    def __init__(self, tag):
        self.tag = tag

    @property
    def code(self):
        return self.tag[0]

    @property
    def value(self):
        return self.tag[1]

    @property
    def ispoint(self):
        return self.code == 10

    def __str__(self):
        if self.ispoint:
            code, value = self.tag
            s = []
            for coord in value:
                s.append(strtag((code, coord)))
                code += 10
            return "".join(s)
        else:
            return strtag(self.tag)
