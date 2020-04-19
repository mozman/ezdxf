# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from typing import Dict, Any
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

__all__ = ['readfile', 'load', 'document']


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

    def _setup_doc(self) -> Drawing:
        doc = Drawing(dxfversion=self.specs.version)
        doc.encoding = self.specs.encoding
        doc.header = HeaderSection.new()

        # Setup basic header variables not stored in the header section of the DWG file.
        doc.header['$ACADVER'] = self.specs.version
        doc.header['$ACADMAINTVER'] = self.specs.maintenance_release_version
        doc.header['$DWGCODEPAGE'] = codepage.tocodepage(self.specs.encoding)

        doc.classes = ClassesSection(doc)
        # doc.tables = TablesSection(doc)
        # doc.blocks = BlocksSection(doc)
        # doc.entities = EntitySection(doc)
        # doc.objects = ObjectsSection(doc)
        # doc.acdsdata = AcDsDataSection(doc)
        return doc

    def load(self):
        self.load_header()
        self.load_classes()
        self.load_objects_map()
        self.load_objects_directory()

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

    def load_objects_map(self) -> None:
        section_data = load_objects_map(self.specs, self.data, self.crc_check)
        self.objects_map = dict(section_data.handles())

    def load_objects_directory(self) -> None:
        pass

    def store_header(self):
        pass

    def store_tables(self) -> None:
        pass

    def store_blocks(self) -> None:
        pass

    def store_objects(self) -> None:
        pass
