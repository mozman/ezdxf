# Purpose: sections module
# Created: 12.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, List, Iterable
import logging
from collections import OrderedDict

from ezdxf.lldxf.const import DXFStructureError, DXF12

from .header import HeaderSection
from .tables2 import TablesSection
from .blocks2 import BlocksSection
from .classes2 import ClassesSection
from .objects2 import ObjectsSection
from .entities2 import EntitySection

if TYPE_CHECKING:
    from ezdxf.eztypes import SectionType, TagWriter
    from ezdxf.drawing2 import Drawing

logger = logging.getLogger('ezdxf')


class Sections:
    def __init__(self, doc: 'Drawing' = None, sections: Dict = None, header: HeaderSection = None):
        self._sections = OrderedDict()  # type: Dict[str, SectionType]
        self._sections['HEADER'] = header or HeaderSection.new()

        # unsupported means: the section data is stored as DXFTag collection
        self.unsupported_sections = []

        if sections:
            self.load(sections, doc)
        else:
            self.setup(doc)

    def __iter__(self) -> Iterable['SectionType']:
        return iter(self._sections.values())

    @staticmethod
    def key(name: str) -> str:
        return name.upper()

    def setup(self, doc: 'Drawing') -> None:
        self._sections['CLASSES'] = ClassesSection(doc)
        self._sections['TABLES'] = TablesSection(doc)
        self._sections['BLOCKS'] = BlocksSection(doc)
        self._sections['ENTITIES'] = EntitySection(doc)
        self._sections['OBJECTS'] = ObjectsSection(doc)

    def load(self, sections: Dict, doc: 'Drawing') -> None:
        self._sections['TABLES'] = TablesSection(doc, sections.get('TABLES', None))
        block_records = self.get('TABLES')['BLOCK_RECORDS']
        self._sections['BLOCKS'] = BlocksSection(doc, sections.get('BLOCKS', None), block_records)
        self._sections['ENTITIES'] = EntitySection(doc, sections.get('ENTITIES', None))
        self._sections['CLASSES'] = ClassesSection(doc, sections.get('CLASSES', None))
        self._sections['OBJECTS'] = ObjectsSection(doc, sections.get('OBJECTS', None))

        for name, data in sections.items():
            if name not in self._sections:
                self.unsupported_sections.append(sections[name])

    def __contains__(self, item: str) -> bool:
        return Sections.key(item) in self._sections

    def __getattr__(self, key: str) -> 'SectionType':
        try:
            return self._sections[Sections.key(key)]
        except KeyError:  # internal exception
            # DXFStructureError because a requested section is not present, maybe a typo, but usual a hint for an
            # invalid DXF file.
            raise DXFStructureError('{} section not found'.format(key.upper()))

    def get(self, name: str) -> 'SectionType':
        return self._sections.get(Sections.key(name), None)

    def names(self) -> List[str]:
        return list(self._sections.keys())

    def remove_unsupported_sections(self):
        self.unsupported_sections = []

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        dxfversion = tagwriter.dxfversion
        self._sections['HEADER'].export_dxf(tagwriter)
        if dxfversion > DXF12:
            self._sections['CLASSES'].export_dxf(tagwriter)
        self._sections['TABLES'].export_dxf(tagwriter)
        self._sections['BLOCKS'].export_dxf(tagwriter)
        self._sections['ENTITIES'].export_dxf(tagwriter)
        if dxfversion > DXF12:
            self._sections['OBJECTS'].export_dxf(tagwriter)

        for section in self.unsupported_sections:
            self.export_unsupported_section(tagwriter, section)

        tagwriter.write_tag2(0, 'EOF')

    @staticmethod
    def export_unsupported_section(tagwriter: 'TagWriter', entities: Iterable):
        for entity in entities:
            tagwriter.write_tags(entity)

        # ENDSEC not stored in entities
        tagwriter.write_str('  0\nENDSEC\n')
