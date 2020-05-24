# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from typing import Dict, Any, Iterable, Callable
import logging
from collections import OrderedDict
from ezdxf.drawing import Drawing
from ezdxf.tools import codepage

from ezdxf.sections.header import HeaderSection
from ezdxf.sections.classes import ClassesSection
from ezdxf.sections.tables import TablesSection
from ezdxf.sections.blocks import BlocksSection
from ezdxf.sections.entities import EntitySection
from ezdxf.sections.objects import ObjectsSection
from ezdxf.sections.acdsdata import AcDsDataSection
from ezdxf.entities import DXFEntity, XData

from .const import *
from .fileheader import FileHeader
from .header_section import load_header_section, HEADER_VARS_TO_RESOLVE
from .classes_section import load_classes_section
from .objects_section import load_objects_map
from .objects import ObjectsDirectory
from .objects import DwgAppID, load_table_handles, DwgTextStyle, DwgLayer, DwgLinetype

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

        # Entity Directory
        self.objects_directory: ObjectsDirectory = ObjectsDirectory()

        self.table_section = dict()
        self.block_section = dict()
        self.object_section = dict()
        self.resolve_resources()

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

        self.set_dxf_header_vars()

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
        objects_map = dict(section_data.handles())
        self.objects_directory.load(self.specs, self.data, objects_map, self.crc_check)

    def load_tables(self) -> None:
        self.load_table('APPID', entry_factory=DwgAppID, dxf_table=self.doc.appids)
        self.load_table('STYLE', entry_factory=DwgTextStyle, dxf_table=self.doc.styles)
        # self.load_table('LTYPE', entry_factory=DwgLinetype, dxf_table=self.doc.linetypes)
        # to resolve 'color_handle' in LAYER the %COLORS_DICTIONARY is required
        self.load_table('LAYER', entry_factory=DwgLayer, dxf_table=self.doc.layers)

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
        try:  # load table control object
            data = objects[handle]
        except KeyError:
            raise DwgCorruptedTableSection(f'{name} table control not found in objects map.')
        else:  # load table entries
            for handle in load_table_handles(self.specs, data, handle):
                try:
                    data = objects[handle]
                except KeyError:
                    raise DwgCorruptedTableSection(f'{name} #{handle} not found in objects map.')
                else:
                    dwg_object = entry_factory(self.specs, data, handle)
                    dwg_object.update_dxfname(self.dxf_object_types)
                    yield dwg_object.dxf(dxffactory)

    def set_dxf_header_vars(self):
        dxf_header = self.doc.header
        entitydb = self.entitydb
        for name, value in self.raw_header_vars.items():
            # Set only supported DXF header vars, a new HEADER section
            # contains for all supported DXF header vars a default value.
            if name in dxf_header:
                if name in HEADER_VARS_TO_RESOLVE and value in entitydb:
                    value = entitydb.get(value).dxf.name
                dxf_header[name] = value

    def resolve_resources(self) -> None:
        """
        DWG loader uses handles instead of names for resources:

            - layer
            - linetype
            - style
            - dimstyle
            - appids in XDATA

        """
        def resolve_color_handles():
            for layer in self.doc.layers:
                if hasattr(layer, 'color_handle'):
                    handle = layer.color_handle
                    delattr(layer, 'color_handle')
                    color = entitydb.get(handle)
                    if color:
                        # todo: set layer color attributes from AcDbColor object
                        pass

        def handle_to_attrib(entity: 'DXFEntity', name: str):
            if entity.dxf.hasattr(name):
                handle = entity.dxf.get(name)
                resource = entitydb.get(handle)
                if resource:
                    entity.dxf.set(name, resource.dxf.name)
                else:
                    logger.debug(f'DWG Loader: Undefined resource for {name} handle #{handle}.')
                    entity.dxf.discard(name)

        entitydb = self.entitydb
        resolve_color_handles()
        for entity in entitydb.values():
            handle_to_attrib(entity, 'layer')
            handle_to_attrib(entity, 'linetype')
            handle_to_attrib(entity, 'style')
            handle_to_attrib(entity, 'dimstyle')
            if entity.xdata:
                # replace app handles by app names
                old_xdata = entity.xdata.data
                new_xdata = OrderedDict()
                for app_handle, data in old_xdata.items():
                    appid = entitydb.get(app_handle)
                    if appid:
                        new_xdata[appid.dxf.name] = data
                    else:
                        logger.debug(f'DWG Loader: Undefined AppID for app handle #{app_handle}.')
                entity.xdata.data = new_xdata
