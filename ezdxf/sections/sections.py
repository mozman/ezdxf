# Purpose: sections module
# Created: 12.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, List, Iterable
import logging

from ezdxf.lldxf.const import DXFStructureError

from .header import HeaderSection
from .tables import TablesSection
from .blocks import BlocksSection
from .classes import ClassesSection
from .objects import ObjectsSection
from .entities import EntitySection
from .unsupported import UnsupportedSection


if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, SectionType, TagWriter


logger = logging.getLogger('ezdxf')
KNOWN_SECTIONS = ('HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'THUMBNAILIMAGE', 'ACDSDATA')


class Sections:
    def __init__(self, sections: Dict, doc: 'Drawing', header: HeaderSection = None):
        self._sections = {
            'HEADER': header if header is not None else HeaderSection.load(tags=None)}  # type: Dict[str, SectionType]
        self._setup_sections(sections, doc)

    def __iter__(self) -> Iterable['SectionType']:
        return iter(self._sections.values())

    @staticmethod
    def key(name: str) -> str:
        return name.upper()

    def _setup_sections(self, sections: Dict, doc: 'Drawing') -> None:
        # required sections
        self._sections['TABLES'] = TablesSection(sections.get('TABLES', None), doc)
        self._sections['BLOCKS'] = BlocksSection(sections.get('BLOCKS', None), doc)
        self._sections['ENTITIES'] = EntitySection(sections.get('ENTITIES', None), doc)
        if doc.dxfversion > 'AC1009':
            # required sections
            self._sections['CLASSES'] = ClassesSection(sections.get('CLASSES', None), doc)
            self._sections['OBJECTS'] = ObjectsSection(sections.get('OBJECTS', None), doc)
            # sections just stored, if exists
            if 'THUMBNAILIMAGE' in sections:
                self._sections['THUMBNAILIMAGE'] = UnsupportedSection(sections['THUMBNAILIMAGE'], doc)
            if 'ACDSDATA' in sections:
                self._sections['ACDSDATA'] = UnsupportedSection(sections['ACDSDATA'], doc)

        for section_name in sections.keys():
            if section_name not in KNOWN_SECTIONS:
                logging.info('Found unknown SECTION: "{}", removed by ezdxf on saving!'.format(section_name))

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

    def write(self, tagwriter: 'TagWriter') -> None:
        write_order = list(KNOWN_SECTIONS)

        unknown_sections = frozenset(self._sections.keys()) - frozenset(KNOWN_SECTIONS)
        if unknown_sections:
            write_order.extend(unknown_sections)

        written_sections = []
        for section_name in KNOWN_SECTIONS:
            section = self._sections.get(section_name, None)
            if section is not None:
                section.write(tagwriter)
                written_sections.append(section.name)

        tagwriter.write_tag2(0, 'EOF')

    def delete_section(self, name: str) -> None:
        """
        Delete a complete section, delete only unnecessary sections like 'THUMBNAILIMAGE' or 'ACDSDATA', else the DXF
        file is corrupted.

        """
        del self._sections[Sections.key(name)]
