# Purpose: acdsdata section manager
# Created: 05.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
"""
ACDSDATA entities have NO handles, therefor they can not be stored in the drawing entity database.
every routine written until now (2014-05-05), expects entities with valid handle - fuck you autodesk

section structure (work in progress):
0 <str> SECTION
2 <str> ACDSDATA
70 <int> 2 # flag?
71 <int> 6 # count of following ACDSSCHEMA entities ??? no, just another flag

0 <str> ACDSSCHEMA           # dxftype: schema definition
90 <int> 0                   # schema number 0, 1, 2, 3 ...
1 <str> AcDb3DSolid_ASM_Data # schema name

2 <str> AcDbDs::ID           # subsection name
280 <int> 10                 # subsection type 10 = ???
91 <int> 8                   # data ???

2 <str> ASM_Data             # subsection name
280 <int> 15                 # subsection type
91 <int> 0                   # data ???
101 <str> ACDSRECORD         # data
95 <int> 0
90 <int> 2
...

0 <str> ACDSSCHEMA
90 <int> 1
1 <str> AcDb_Thumbnail_Schema
...

0 <str> ACDSSCHEMA
90 <int> 2
1 <str> AcDbDs::TreatedAsObjectDataSchema
...

0 <str> ACDSSCHEMA
90 <int> 3
1 <str> AcDbDs::LegacySchema
2 <str> AcDbDs::Legacy
280 <int> 1
91 <int> 0

0 <str> ACDSSCHEMA
90 <int> 4
1 <str> AcDbDs::IndexedPropertySchema
2 <str> AcDs:Indexable
280 <int> 1
91 <int> 0

0 <str> ACDSSCHEMA
90 <int> 5
1 <str> AcDbDs::HandleAttributeSchema
2 <str> AcDbDs::HandleAttribute
280 <int> 7
91 <int> 1
284 <int> 1

0 <str> ACDSRECORD               # dxftype: data record
90 <int> 0                       # ??? flag
2 <str> AcDbDs::ID               # subsection name
280 <int> 10                     # subsection type 10 = handle to owner entity, 3DSOLID???
320 <str> 339                    # handle
2 <str> ASM_Data                 # subsection name
280 <int> 15                     # subsection type 15 = binary data
94 <int> 1088                    # size of data
310 <binary encoded data>        # data
310 <binary encoded data>        # data
...

0 <str> ENDSEC
"""
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice
from .tags import TagGroups, DXFStructureError, write_tags, Tags


class AcDsDataSection(object):
    name = 'acdsdata'

    def __init__(self, tags, drawing):
        self.entities = []  # stores AcDsData objects
        self.section_info = []
        self.drawing = drawing
        if tags is not None:
            self._build(tags)

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    @property
    def entitydb(self):
        return self.drawing.entitydb

    def _build(self, tags):
        if tags[0] != (0, 'SECTION') or tags[1] != (2, self.name.upper()) or tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        if len(tags) == 3:  # empty entities section
            return

        start_index = 2
        while tags[start_index].code != 0:
            self.section_info.append(tags[start_index])
            start_index += 1

        for group in TagGroups(islice(tags, start_index, len(tags)-1)):
            self._append_entity(AcDsData(Tags(group)))  # tags have no subclasses

    def _append_entity(self, entity):
        cls = ACDSDATA_TYPES.get(entity.dxftype())
        if cls is not None:
            entity = cls(entity.tags)
        self.entities.append(entity)

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        write_tags(stream, self.section_info)
        for entity in self.entities:
            entity.write(stream)
        stream.write("  0\nENDSEC\n")


class AcDsData(object):
    def __init__(self, tags):
        self.tags = tags

    def write(self, stream):
        write_tags(stream, self.tags)

    def dxftype(self):
        return self.tags[0].value


class Section(Tags):
    @property
    def name(self):
        return self[0].value

    @property
    def type(self):
        return self[1].value

    @property
    def data(self):
        return self[2:]


class AcDsRecord(object):
    def __init__(self, tags):
        self._dxftype = tags[0]
        self.flags = tags[1]
        self.sections = [Section(tags) for tags in TagGroups(islice(tags, 2, None), splitcode=2)]

    def dxftype(self):
        return self._dxftype.value

    def has_section(self, name):
        return self.get_section(name, default=None) is not None

    def get_section(self, name, default=KeyError):
        for section in self.sections:
            if section.name == name:
                return section
        if default is KeyError:
            raise KeyError(name)
        else:
            return default

    def __getitem__(self, name):
        return self.get_section(name)

    def _write_header(self, stream):
        write_tags(stream, Tags([self._dxftype, self.flags]))

    def write(self, stream):
        self._write_header(stream)
        for section in self.sections:
            write_tags(stream, section)

ACDSDATA_TYPES = {
    'ACDSRECORD': AcDsRecord,
}