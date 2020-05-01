# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from typing import Dict, Any, Iterable, Callable
import logging
from ezdxf.drawing import Drawing
from ezdxf.tools import codepage

from ezdxf.sections.header import HeaderSection
from ezdxf.sections.classes import ClassesSection
from ezdxf.sections.tables import TablesSection
from ezdxf.sections.blocks import BlocksSection
from ezdxf.sections.entities import EntitySection
from ezdxf.sections.objects import ObjectsSection
from ezdxf.sections.acdsdata import AcDsDataSection

from .const import *
from .fileheader import FileHeader
from .header_section import load_header_section
from .classes_section import load_classes_section
from .objects_section import load_objects_map
from .objects import ObjectsDirectory
from .objects import DwgAppID, load_table_handles

__all__ = ['readfile', 'load', 'document']
logger = logging.getLogger('ezdxf')


def readfile(filename: str, crc_check=False) -> 'Drawing':
    """ Read DXF Document from DWG file. """
    data = open(filename, 'rb').read()
    return load(data, crc_check)


def load(data: bytes, crc_check=False) -> Drawing:
    """ Load DXF Document from DWG data. """
    doc = document(data, crc_check)
    return doc.doc


def document(data: bytes, crc_check=False) -> 'DwgDocument':
    """ Returns DWG Document loader object - just for testing. """
    doc = DwgDocument(data, crc_check=crc_check)
    doc.load()
    return doc


class DwgDocument:
    def __init__(self, data: Bytes, crc_check=False):
        # Raw DWG data
        self.data = memoryview(data)

        # True to perform CRC checks, False for faster loading without CRC checks
        self.crc_check = crc_check

        # DWG file header - version, encoding, file location of data sections
        self.specs = FileHeader(data, crc_check=crc_check)

        # DXF Document
        self.doc: Drawing = self._setup_doc()

        # All data stored in header section
        self.raw_header_vars: Dict[str, Any] = dict()

        # Store DXF object types by class number
        self.dxf_object_types: Dict[int, str] = dict()

        # Entity handle to file location mapping
        self.objects_map: Dict[str, int] = dict()

        # Entity Directory
        self.objects_directory: ObjectsDirectory = ObjectsDirectory()

        self.table_section = dict()
        self.block_section = dict()
        self.object_section = dict()

    @property
    def entitydb(self):
        return self.doc.entitydb

    def _setup_doc(self) -> Drawing:
        doc = Drawing(dxfversion=self.specs.version)
        doc.encoding = self.specs.encoding
        doc.header = HeaderSection.new()

        # Setup basic header variables not stored in the header section of the DWG file.
        doc.header['$ACADVER'] = self.specs.version
        doc.header['$ACADMAINTVER'] = self.specs.maintenance_release_version
        doc.header['$DWGCODEPAGE'] = codepage.tocodepage(self.specs.encoding)

        doc.classes = ClassesSection(doc)
        doc.tables = TablesSection(doc)
        # doc.blocks = BlocksSection(doc)
        # doc.entities = EntitySection(doc)
        # doc.objects = ObjectsSection(doc)
        # doc.acdsdata = AcDsDataSection(doc)
        return doc

    def load(self):
        self.load_header()
        self.load_classes()
        self.load_objects_directory()
        self.load_tables()

        # copy data to DXF document
        self.store_header()
        self.store_tables()
        self.store_blocks()
        self.store_objects()

    def load_header(self) -> None:
        hdr_section = load_header_section(self.specs, self.data, self.crc_check)
        self.raw_header_vars = hdr_section.load_header_vars()

    def load_classes(self) -> None:
        cls_section = load_classes_section(self.specs, self.data, self.crc_check)
        for class_num, dxfclass in cls_section.load_classes():
            self.doc.classes.register(dxfclass)
            self.dxf_object_types[class_num] = dxfclass.dxf.name

    def load_objects_directory(self) -> None:
        section_data = load_objects_map(self.specs, self.data, self.crc_check)
        self.objects_map = dict(section_data.handles())
        self.objects_directory.load(self.specs, self.data, self.objects_map, self.crc_check)

    def load_tables(self) -> None:
        self.load_table('APPID', entry_factory=DwgAppID, dxf_table=self.doc.appids)

    def load_table(self, name: str, entry_factory: Callable, dxf_table) -> None:
        add_to_entitydb = self.entitydb.add
        add_to_table = dxf_table.add_entry
        try:
            handle = self.raw_header_vars[f'%{name}_TABLE']
        except KeyError:
            raise DwgCorruptedTableSection(f'{name} table handle not present.')
        else:
            dxf_table.init_table_head(name, handle)
            add_to_entitydb(dxf_table.head)
            for entry in self.load_table_entries(handle, name=name, entry_factory=entry_factory):
                add_to_entitydb(entry)
                add_to_table(entry)

    def load_table_entries(self, handle: str, name: str, entry_factory: Callable) -> Iterable:
        dxffactory = self.doc.dxffactory
        objects = self.objects_directory
        try:
            data = objects[handle]
        except KeyError:
            raise DwgCorruptedTableSection(f'{name} table control not found in objects map.')
        else:
            for handle in load_table_handles(self.specs, data, handle):
                try:
                    data = objects[handle]
                except KeyError:
                    raise DwgCorruptedTableSection(f'{name} #{handle} not found in objects map.')
                else:
                    dwg_object = entry_factory(self.specs, data, handle)
                    dwg_object.update_dxfname(self.dxf_object_types)
                    yield dwg_object.dxf(dxffactory)

    def store_header(self):
        pass

    def store_tables(self) -> None:
        pass

    def store_blocks(self) -> None:
        pass

    def store_objects(self) -> None:
        pass
