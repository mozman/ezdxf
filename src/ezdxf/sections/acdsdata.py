# Purpose: acdsdata section manager
# Copyright (c) 2014-2022, Manfred Moitzi
# License: MIT License
"""
ACDSDATA entities have NO handles, therefore they can not be stored in the
drawing entity database.

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
280 <int> 10                     # subsection type 10 = handle to owner entity, 3DSOLID/REGION
320 <str> 339                    # handle
2 <str> ASM_Data                 # subsection name
280 <int> 15                     # subsection type 15 = binary data
94 <int> 1088                    # size of data
310 <binary encoded data>        # data
310 <binary encoded data>        # data
...

0 <str> ENDSEC
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, Iterable, List, Any, Optional
import abc
from itertools import islice

from ezdxf.lldxf.tags import group_tags, Tags
from ezdxf.lldxf.const import DXFKeyError, DXFStructureError

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing


class AcDsEntity(abc.ABC):
    @abc.abstractmethod
    def export_dxf(self, tagwriter: TagWriter):
        ...

    @abc.abstractmethod
    def dxftype(self) -> str:
        ...


class AcDsDataSection:
    name = "ACDSDATA"

    def __init__(self, doc: Drawing, entities: Iterable[Tags] = None):
        self.doc = doc
        self.entities: List[AcDsEntity] = []
        self.section_info = Tags()
        if entities is not None:
            self.load_tags(iter(entities))

    @property
    def is_valid(self):
        return len(self.section_info)

    def load_tags(self, entities: Iterator[Tags]) -> None:
        section_head = next(entities)
        if section_head[0] != (0, "SECTION") or section_head[1] != (
            2,
            "ACDSDATA",
        ):
            raise DXFStructureError(
                "Critical structure error in ACDSDATA section."
            )

        self.section_info = section_head
        for entity in entities:
            self.append(AcDsData(entity))  # tags have no subclasses

    def append(self, entity: AcDsData) -> None:
        cls = ACDSDATA_TYPES.get(entity.dxftype(), AcDsData)
        data = cls(entity.tags)
        self.entities.append(data)

    def export_dxf(self, tagwriter: TagWriter) -> None:
        if not self.is_valid:
            return
        tagwriter.write_tags(self.section_info)
        for entity in self.entities:
            entity.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    @property
    def acdsrecords(self) -> Iterable[AcDsRecord]:
        return (
            entity for entity in self.entities if isinstance(entity, AcDsRecord)
        )

    def get_acis_data(self, handle: str) -> List[bytes]:
        asm_record = self.find_acis_record(handle)
        if asm_record is not None:
            return get_acis_data(asm_record)
        return []

    def set_acis_data(self, handle, sab_data: bytes) -> None:
        asm_record = self.find_acis_record(handle)
        if asm_record is not None:
            set_acis_data(asm_record, sab_data)

    def del_acis_data(self, handle) -> None:
        asm_record = self.find_acis_record(handle)
        if asm_record is not None:
            self.entities.remove(asm_record)

    def find_acis_record(self, handle: str) -> Optional[AcDsRecord]:
        for record in self.acdsrecords:
            if is_acis_data(record) and acis_entity_handle(record) == handle:
                return record
        return None


class AcDsData(AcDsEntity):
    def __init__(self, tags: Tags):
        self.tags = tags

    def export_dxf(self, tagwriter: TagWriter):
        tagwriter.write_tags(self.tags)

    def dxftype(self) -> str:
        return self.tags[0].value


class Section(Tags):
    @property
    def name(self) -> str:
        return self[0].value

    @property
    def type(self) -> str:
        return self[1].value

    @property
    def data(self) -> Tags:
        return Tags(self[2:])


class AcDsRecord(AcDsEntity):
    def __init__(self, tags: Tags):
        self._dxftype = tags[0]
        self.flags = tags[1]
        self.sections = [
            Section(group)
            for group in group_tags(islice(tags, 2, None), splitcode=2)
        ]

    def dxftype(self) -> str:
        return "ACDSRECORD"

    def has_section(self, name: str) -> bool:
        return self.get_section(name, default=None) is not None

    def get_section(self, name: str, default: Any = DXFKeyError) -> Section:
        for section in self.sections:
            if section.name == name:
                return section
        if default is DXFKeyError:
            raise DXFKeyError(name)
        else:
            return default

    def __len__(self):
        return len(self.sections)

    def __getitem__(self, item) -> Section:
        return self.sections[item]

    def _write_header(self, tagwriter: TagWriter) -> None:
        tagwriter.write_tags(Tags([self._dxftype, self.flags]))

    def export_dxf(self, tagwriter: TagWriter) -> None:
        self._write_header(tagwriter)
        for section in self.sections:
            tagwriter.write_tags(section)


def get_acis_data(record: AcDsRecord) -> List[bytes]:
    try:
        asm_data = record.get_section("ASM_Data")
    except DXFKeyError:  # no data stored
        return []
    else:
        return [tag.value for tag in asm_data if tag.code == 310]


def is_acis_data(record: AcDsRecord) -> bool:
    return record.has_section("ASM_Data")


def acis_entity_handle(record: AcDsRecord) -> str:
    try:
        section = record.get_section("AcDbDs::ID")
    except DXFKeyError:  # not present
        return ""
    return section.get_first_value(320, "")


def set_acis_data(record: AcDsRecord, data: bytes) -> None:
    pass


ACDSDATA_TYPES = {
    "ACDSRECORD": AcDsRecord,
}


DEFAULT_SETUP = """0
SECTION
2
ACDSDATA
70
2
71
2
0
ACDSSCHEMA
90
0
1
AcDb_Thumbnail_Schema
2
AcDbDs::ID
280
10
91
8
2
Thumbnail_Data
280
15
91
0
101
ACDSRECORD
95
0
90
2
2
AcDbDs::TreatedAsObjectData
280
1
291
1
101
ACDSRECORD
95
0
90
3
2
AcDbDs::Legacy
280
1
291
1
101
ACDSRECORD
1
AcDbDs::ID
90
4
2
AcDs:Indexable
280
1
291
1
101
ACDSRECORD
1
AcDbDs::ID
90
5
2
AcDbDs::HandleAttribute
280
7
282
1
0
ACDSSCHEMA
90
1
1
AcDb3DSolid_ASM_Data
2
AcDbDs::ID
280
10
91
8
2
ASM_Data
280
15
91
0
101
ACDSRECORD
95
1
90
2
2
AcDbDs::TreatedAsObjectData
280
1
291
1
101
ACDSRECORD
95
1
90
3
2
AcDbDs::Legacy
280
1
291
1
101
ACDSRECORD
1
AcDbDs::ID
90
4
2
AcDs:Indexable
280
1
291
1
101
ACDSRECORD
1
AcDbDs::ID
90
5
2
AcDbDs::HandleAttribute
280
7
282
1
0
ACDSSCHEMA
90
2
1
AcDbDs::TreatedAsObjectDataSchema
2
AcDbDs::TreatedAsObjectData
280
1
91
0
0
ACDSSCHEMA
90
3
1
AcDbDs::LegacySchema
2
AcDbDs::Legacy
280
1
91
0
0
ACDSSCHEMA
90
4
1
AcDbDs::IndexedPropertySchema
2
AcDs:Indexable
280
1
91
0
0
ACDSSCHEMA
90
5
1
AcDbDs::HandleAttributeSchema
2
AcDbDs::HandleAttribute
280
7
91
1
284
1
"""
# (0, ENDSEC) must be omitted!


def new_acds_data_section(doc: Drawing) -> AcDsDataSection:
    if doc.dxfversion >= "AC1027":
        return AcDsDataSection(doc, group_tags(Tags.from_text(DEFAULT_SETUP)))
    else:
        return AcDsDataSection(doc)
