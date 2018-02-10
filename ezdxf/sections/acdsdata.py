# Purpose: acdsdata section manager
# Created: 05.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
"""
ACDSDATA entities have NO handles, therefor they can not be stored in the drawing entity database.
every routine written until now (2014-05-05), expects entities with valid handle

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
__author__ = "mozman <me@mozman.at>"

from itertools import islice
from ..lldxf.tags import group_tags, Tags
from ..lldxf.const import DXFKeyError, DXFStructureError


class AcDsDataSection(object):
    name = 'ACDSDATA'

    def __init__(self, entities, drawing):
        self.entities = []  # stores AcDsData objects
        self.section_info = []
        self.drawing = drawing
        if entities is not None:
            self._build(iter(entities))

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    @property
    def entitydb(self):
        return self.drawing.entitydb

    def _build(self, entities):
        section_head = next(entities)
        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, 'ACDSDATA'):
            raise DXFStructureError("Critical structure error in ACDSDATA section.")

        self.section_info = section_head
        for entity in entities:
            self._append_entity(AcDsData(entity))  # tags have no subclasses

    def _append_entity(self, entity):
        cls = ACDSDATA_TYPES.get(entity.dxftype())
        if cls is not None:
            entity = cls(entity.tags)
        self.entities.append(entity)

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\nACDSDATA\n")
        tagwriter.write_tags(self.section_info)
        for entity in self.entities:
            entity.write(tagwriter)
        tagwriter.write_tag2(0, 'ENDSEC')


class AcDsData(object):
    def __init__(self, tags):
        self.tags = tags

    def write(self, tagwriter):
        tagwriter.write_tags(self.tags)

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
        self.sections = [Section(tags) for tags in group_tags(islice(tags, 2, None), splitcode=2)]

    def dxftype(self):
        return self._dxftype.value

    def has_section(self, name):
        return self.get_section(name, default=None) is not None

    def get_section(self, name, default=DXFKeyError):
        for section in self.sections:
            if section.name == name:
                return section
        if default is DXFKeyError:
            raise DXFKeyError(name)
        else:
            return default

    def __getitem__(self, name):
        return self.get_section(name)

    def _write_header(self, tagwriter):
        tagwriter.write_tags(Tags([self._dxftype, self.flags]))

    def write(self, tagwriter):
        self._write_header(tagwriter)
        for section in self.sections:
            tagwriter.write_tags(section)


ACDSDATA_TYPES = {
    'ACDSRECORD': AcDsRecord,
}
