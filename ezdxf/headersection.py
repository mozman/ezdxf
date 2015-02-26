# Purpose: manage header section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import OrderedDict

from .c23 import ustr
from .dxftag import strtag
from .tags import TagGroups, Tags, DXFStructureError

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


class CustomVars():
    def __init__(self):
        self.properties = list()

    def append(self, tag, value):
        # custom properties always stored as strings
        self.properties.append((tag, ustr(value)))

    def get(self, tag, default=None):
            for item in self.properties:
                if item[0] == tag:
                    return item[1]
            else:
                return default

    def has_tag(self, tag):
        return self.get(tag) is not None

    def delete(self, tag):
            for item in self.properties:
                if item[0] == tag:
                    self.properties.remove(item)
                    return
            raise ValueError("Tag '%s' does not exist" % tag)

    def write(self, stream):
        for item in self.properties:
            stream.write("  9\n$CUSTOMPROPERTYTAG\n  1\n%s\n" % item[0])
            stream.write("  9\n$CUSTOMPROPERTY\n  1\n%s\n" % item[1])


class HeaderSection(object):
    MIN_HEADER_TAGS = Tags.from_text(MIN_HEADER_TEXT)
    name = 'header'

    def __init__(self, tags=None):
        if tags is None:
            tags = self.MIN_HEADER_TAGS
        self.hdrvars = OrderedDict()
        self.customvars = CustomVars()
        self._build(tags)

    def set_headervar_factory(self, factory):
        self._headervar_factory = factory

    def __contains__(self, key):
        return key in self.hdrvars

    def _build(self, tags):
        if tags[0] != (0, 'SECTION') or \
           tags[1] != (2, 'HEADER') or \
           tags[-1] != (0, 'ENDSEC'):
           raise DXFStructureError("Critical structure error in HEADER section.")

        if len(tags) == 3:  # DXF file with empty header section
            return
        groups = TagGroups(tags[2:-1], splitcode=9)
        custom_tag = None
        custom_tag_value = None
        for group in groups:
            name = group[0].value
            value = group[1]
            if name == '$CUSTOMPROPERTYTAG':
                custom_tag = value.value
            elif name == '$CUSTOMPROPERTY':
                custom_tag_value = value.value
            else:
                self.hdrvars[name] = HeaderVar(value)

            # Set custom Property
            if custom_tag is not None and custom_tag_value is not None:
                self.customvars.append(custom_tag, custom_tag_value)
                custom_tag = None
                custom_tag_value = None

    def write(self, stream):
        def _write(name, value):
            stream.write("  9\n%s\n" % name)
            stream.write(ustr(value))

        stream.write("  0\nSECTION\n  2\nHEADER\n")
        for name, value in self.hdrvars.items():
            _write(name, value)

        self.customvars.write(stream)
        stream.write("  0\nENDSEC\n")

    def __getitem__(self, key):
        return self.hdrvars[key].value

    def get(self, key, default=None):
        if key in self.hdrvars:
            return self.__getitem__(key)
        else:
            return default

    def __setitem__(self, key, value):
        tags = self._headervar_factory(key, value)
        self.hdrvars[key] = HeaderVar(tags)

    def __delitem__(self, key):
        del self.hdrvars[key]


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
