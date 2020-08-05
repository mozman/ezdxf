# Created: 11.03.2011
# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, TextIO, BinaryIO, Iterable, Union, Sequence, Tuple, Callable, cast
from typing import Optional
from datetime import datetime
import io
import base64
import logging
from itertools import chain

from ezdxf.lldxf.const import acad_release, BLK_XREF, BLK_EXTERNAL, DXFValueError, acad_release_to_dxf_version
from ezdxf.lldxf.const import DXF13, DXF14, DXF2000, DXF2007, DXF12, DXF2013, \
    versions_supported_by_save, versions_supported_by_new
from ezdxf.lldxf.const import DXFVersionError
from ezdxf.lldxf.loader import load_dxf_structure, fill_database, SectionDict
from ezdxf.lldxf import repair
from ezdxf.lldxf.tagwriter import TagWriter, BinaryTagWriter

from ezdxf.entitydb import EntityDB
from ezdxf.entities.factory import EntityFactory
from ezdxf.layouts.layouts import Layouts
from ezdxf.tools.codepage import tocodepage, toencoding
from ezdxf.tools.juliandate import juliandate
from ezdxf.options import options

from ezdxf.tools import guid
from ezdxf.tracker import Tracker
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.render.dimension import DimensionRenderer

from ezdxf.sections.header import HeaderSection
from ezdxf.sections.classes import ClassesSection
from ezdxf.sections.tables import TablesSection
from ezdxf.sections.blocks import BlocksSection
from ezdxf.sections.entities import EntitySection, StoredSection
from ezdxf.sections.objects import ObjectsSection
from ezdxf.sections.acdsdata import AcDsDataSection

from ezdxf.entities.dxfgroups import GroupCollection
from ezdxf.entities.material import MaterialCollection
from ezdxf.entities.mleader import MLeaderStyleCollection
from ezdxf.entities.mline import MLineStyleCollection

logger = logging.getLogger('ezdxf')
MANAGED_SECTIONS = {'HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'ACDSDATA'}

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFTag, Table, ViewportTable, VPort
    from ezdxf.eztypes import Dictionary, BlockLayout, Layout
    from ezdxf.eztypes import DXFEntity, Layer, Auditor

    LayoutType = Union[Layout, BlockLayout]

TFilterStack = Sequence[Sequence[Callable[[Iterable['DXFTag']], Iterable['DXFTag']]]]


# [(raw_tag_filter1, raw_tag_filter2), (compiled_tag_filter1, )]

class Drawing:
    def __init__(self, dxfversion=DXF2013):
        self.entitydb = EntityDB()
        self.dxffactory = EntityFactory(self)
        self.tracker = Tracker()
        target_dxfversion = dxfversion.upper()
        self._dxfversion: str = acad_release_to_dxf_version.get(target_dxfversion, target_dxfversion)
        if self._dxfversion not in versions_supported_by_new:
            raise DXFVersionError(f'Unsupported DXF version "{self.dxfversion}".')
        # Store original dxf version if loaded (and maybe converted R13/14) from file.
        self._loaded_dxfversion: Optional[str] = None
        self.encoding: str = 'cp1252'  # read/write
        self.filename: Optional[str] = None

        # named objects dictionary
        self.rootdict: 'Dictionary' = None

        # DXF sections
        self.header: HeaderSection = None
        self.classes: ClassesSection = None
        self.tables: TablesSection = None
        self.blocks: BlocksSection = None
        self.entities: EntitySection = None
        self.objects: ObjectsSection = None

        # DXF R2013 and later
        self.acdsdata: AcDsDataSection = None

        self.stored_sections = []
        self.layouts: Layouts = None
        self.groups: GroupCollection = None
        self.materials: MaterialCollection = None
        self.mleader_styles: MLeaderStyleCollection = None
        self.mline_styles: MLineStyleCollection = None
        self._acad_compatible = True  # will generated DXF file compatible with AutoCAD
        self._dimension_renderer = DimensionRenderer()  # set DIMENSION rendering engine
        self._acad_incompatibility_reason = set()  # avoid multiple warnings for same reason
        # Don't create any new entities here:
        # New created handles could collide with handles loaded from DXF file.
        assert len(self.entitydb) == 0

    @classmethod
    def new(cls, dxfversion: str = DXF2013) -> 'Drawing':
        """ Create new drawing. Package users should use the factory function :func:`ezdxf.new`.
        (internal API)
        """
        doc = cls(dxfversion)
        doc._setup()
        return doc

    def _setup(self):
        self.header = HeaderSection.new()
        self.classes = ClassesSection(self)
        self.tables = TablesSection(self)
        self.blocks = BlocksSection(self)
        self.entities = EntitySection(self)
        self.objects = ObjectsSection(self)
        self.acdsdata = AcDsDataSection(self)  # AcDSData section is not supported for new drawings
        self.rootdict = self.objects.rootdict
        self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables
        self.layouts = Layouts.setup(self)
        self._finalize_setup()

    def _finalize_setup(self):
        """ Common setup tasks for new and loaded DXF drawings. """
        self.groups = GroupCollection(self)
        self.materials = MaterialCollection(self)

        self.mline_styles = MLineStyleCollection(self)
        # all required internal structures are ready
        # now do the stuff to please AutoCAD
        self._create_required_table_entries()

        # mleader_styles requires text styles
        self.mleader_styles = MLeaderStyleCollection(self)
        self._set_required_layer_attributes()
        self._setup_metadata()

    def _create_required_table_entries(self):
        self._create_required_vports()
        self._create_required_linetypes()
        self._create_required_layers()
        self._create_required_styles()
        self._create_required_appids()
        self._create_required_dimstyles()

    def _set_required_layer_attributes(self):
        for layer in self.layers:  # type: Layer
            layer.set_required_attributes()

    def _create_required_vports(self):
        if '*Active' not in self.viewports:
            self.viewports.new('*Active')

    def _create_required_appids(self):
        if 'ACAD' not in self.appids:
            self.appids.new('ACAD')

    def _create_required_linetypes(self):
        linetypes = self.linetypes
        for name in ('ByBlock', 'ByLayer', 'Continuous'):
            if name not in linetypes:
                linetypes.new(name)

    def _create_required_dimstyles(self):
        if 'Standard' not in self.dimstyles:
            self.dimstyles.new('Standard')

    def _create_required_styles(self):
        if 'Standard' not in self.styles:
            self.styles.new('Standard')

    def _create_required_layers(self):
        layers = self.layers
        if '0' not in layers:
            layers.new('0')
        if 'Defpoints' not in layers:
            layers.new('Defpoints', dxfattribs={'plot': 0})  # do not plot
        else:
            # AutoCAD requires a plot flag = 0
            layers.get('Defpoints').dxf.plot = 0

    def _setup_metadata(self):
        self.header['$ACADVER'] = self.dxfversion
        self.header['$TDCREATE'] = juliandate(datetime.now())
        self.reset_fingerprint_guid()
        self.reset_version_guid()

    @property
    def dxfversion(self) -> str:
        """ Get current DXF version. """
        return self._dxfversion

    @dxfversion.setter
    def dxfversion(self, version) -> None:
        """ Set current DXF version. """
        self._dxfversion = self._validate_dxf_version(version)
        self.header['$ACADVER'] = version

    @property
    def output_encoding(self):
        """ Returns required output encoding for writing document to a text streams. """
        return 'utf-8' if self.dxfversion >= DXF2007 else self.encoding

    def _validate_dxf_version(self, version: str) -> str:
        version = version.upper()
        version = acad_release_to_dxf_version.get(version, version)  # translates 'R12' -> 'AC1009'
        if version not in versions_supported_by_save:
            raise DXFVersionError(f'Unsupported DXF version "{version}".')
        if version == DXF12:
            if self._dxfversion > DXF12:
                logger.warning(f'Downgrade from DXF {self.acad_release} to R12 may create an invalid DXF file.')
        elif version < self._dxfversion:
            logger.info(f'Downgrade from DXF {self.acad_release} to {acad_release[version]} can cause lost of features.')
        return version

    @classmethod
    def read(cls, stream: TextIO, legacy_mode: bool = False, filter_stack: TFilterStack = None) -> 'Drawing':
        """ Open an existing drawing. Package users should use the factory function :func:`ezdxf.read`.

        Args:
             stream: text stream yielding text (unicode) strings by readline()
             legacy_mode: apply some low level filters to correct some quirks allowed in legacy (R12) files
             filter_stack: interface to put filters between reading layers, list of callable filters, for now
                           two levels are supported, after low level tagging (DXFVertex) and after compiling tags to
                           DXFVertex and DXFBinaryTag.

                TFilterStack: Sequence[Sequence[Callable[[Iterable[DXFTag]], Iterable[DXFTag]]]]
                e.g. [(raw_tag_filter1, raw_tag_filter2), (compiled_tag_filter1, )]

        """
        from .lldxf.tagger import ascii_tags_loader
        tag_loader = ascii_tags_loader(stream)
        return cls.load(tag_loader, legacy_mode=legacy_mode, filter_stack=filter_stack)

    @classmethod
    def load(cls, tag_loader: Iterable['DXFTag'], legacy_mode: bool = False,
             filter_stack: TFilterStack = None) -> 'Drawing':
        """ Load DXF document from DXF tag loader.

        Args:
             tag_loader: DXF tag loader
             legacy_mode: apply some low level filters to correct some quirks allowed in legacy (R12) files
             filter_stack: interface to put filters between reading layers, list of callable filters, for now
                           two levels are supported, after low level tagging (DXFVertex) and after compiling tags to
                           DXFVertex and DXFBinaryTag.

                TFilterStack: Sequence[Sequence[Callable[[Iterable[DXFTag]], Iterable[DXFTag]]]]
                e.g. [(raw_tag_filter1, raw_tag_filter2), (compiled_tag_filter1, )]

        """
        from .lldxf.tagger import tag_compiler
        raw_tag_filters = []
        compiled_tag_filters = []

        if filter_stack:
            # maybe more levels in the future
            raw_tag_filters, compiled_tag_filters, *_ = filter_stack

        # legacy mode overrides filter_stack
        if legacy_mode:
            raw_tag_filters = [repair.tag_reorder_layer, repair.filter_invalid_yz_point_codes]
            compiled_tag_filters = []

        # low level tag compiler, creates simple tuple like tags DXFTag(group code, value)

        # apply low level filters
        for _filter in raw_tag_filters:
            tag_loader = _filter(tag_loader)

        # compiles vertices and binary tags into DXFVertex() or DXFBinaryTag()
        tag_loader = tag_compiler(tag_loader)

        # apply compiled tags filter
        for _filter in compiled_tag_filters:
            tag_loader = _filter(tag_loader)

        doc = cls()
        doc._load(tag_loader)
        return doc

    @classmethod
    def from_tags(cls, compiled_tags: Iterable['DXFTag']) -> 'Drawing':
        """ Create new drawing from compiled tags. (internal API)"""
        doc = cls()
        doc._load(tagger=compiled_tags)
        return doc

    @classmethod
    def from_section_dict(cls, sections: SectionDict) -> 'Drawing':
        """ Create new drawing from a SectionDict. (internal API)"""
        doc = cls()
        doc._load(sections=sections)
        return doc

    def _load(self, tagger: Optional[Iterable['DXFTag']] = None, sections: Optional[SectionDict] = None):
        if tagger is None and sections is None:
            raise ValueError('DXF tagger or SectionDict required.')

        if sections is None:
            sections = load_dxf_structure(tagger)  # load complete DXF entity structure
        try:  # discard section THUMBNAILIMAGE
            del sections['THUMBNAILIMAGE']
        except KeyError:
            pass
        # -----------------------------------------------------------------------------------
        # create header section:
        # all header tags are the first DXF structure entity
        header_entities = sections.get('HEADER', [None])[0]
        if header_entities is None:
            # create default header, files without header are by default DXF R12
            self.header = HeaderSection.new(dxfversion=DXF12)
        else:
            self.header = HeaderSection.load(header_entities)
        # -----------------------------------------------------------------------------------
        # Missing $ACADVER defaults to DXF R12
        self._dxfversion: str = self.header.get('$ACADVER', DXF12)
        # Store original DXF version of loaded file.
        self._loaded_dxfversion = self._dxfversion
        self.encoding = toencoding(self.header.get('$DWGCODEPAGE', 'ANSI_1252'))
        # get handle seed
        seed: str = self.header.get('$HANDSEED', str(self.entitydb.handles))
        # setup handles
        self.entitydb.handles.reset(seed)
        # store all necessary DXF entities in the drawing database
        fill_database(sections, self.dxffactory)
        # all handles used in the DXF file are known at this point
        # -----------------------------------------------------------------------------------
        # create sections:
        self.classes = ClassesSection(self, sections.get('CLASSES', None))
        self.tables = TablesSection(self, sections.get('TABLES', None))
        # create *Model_Space and *Paper_Space BLOCK_RECORDS
        # BlockSection setup takes care about the rest
        self._create_required_block_records()
        # table records available
        self.blocks = BlocksSection(self, sections.get('BLOCKS', None))

        self.entities = EntitySection(self, sections.get('ENTITIES', None))
        self.objects = ObjectsSection(self, sections.get('OBJECTS', None))
        # only valid for DXF R2013 and later
        self.acdsdata = AcDsDataSection(self, sections.get('ACDSDATA', None))

        for name, data in sections.items():
            if name not in MANAGED_SECTIONS:
                self.stored_sections.append(StoredSection(data))
        # -----------------------------------------------------------------------------------
        if self.dxfversion < DXF12:
            # upgrade to DXF R12
            logger.info('Upgrading drawing to DXF R12.')
            self.dxfversion = DXF12

        # DIMSTYLE: ezdxf uses names for blocks, linetypes and text style as internal data, handles are set at export
        # requires BLOCKS and TABLES section!
        self.tables.resolve_dimstyle_names()

        if self.dxfversion == DXF12:
            # TABLE requires in DXF12 no handle and has no owner tag, but DXF R2000+, requires a TABLE with handle
            # and each table entry has an owner tag, pointing to the TABLE entry
            self.tables.create_table_handles()

        if self.dxfversion in (DXF13, DXF14):
            # upgrade to DXF R2000
            self.dxfversion = DXF2000
            self.create_all_arrow_blocks()

        self.rootdict = self.objects.rootdict
        self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables

        self.layouts = Layouts.load(self)
        self._finalize_setup()

    def create_all_arrow_blocks(self):
        """
        For upgrading DXF R12/13/14 files to R2000, it is necessary to create all used arrow blocks before saving the
        DXF file, else $HANDSEED is not the next available handle, which is a problem for AutoCAD.
        To be save create all known AutoCAD arrows, because references to arrow blocks can be in DIMSTYLE,
        DIMENSION override, LEADER override and maybe other places.

        """
        from ezdxf.render.arrows import ARROWS
        for arrow_name in ARROWS.__acad__:
            ARROWS.create_block(self.blocks, arrow_name)

    def _create_required_block_records(self):
        if '*Model_Space' not in self.block_records:
            self.block_records.new('*Model_Space')
        if '*Paper_Space' not in self.block_records:
            self.block_records.new('*Paper_Space')

    def saveas(self, filename: str, encoding: str = None, fmt: str = 'asc') -> None:
        """
        Set :class:`Drawing` attribute :attr:`filename` to `filename` and write drawing to the file system.
        Override file encoding by argument `encoding`, handle with care, but this option allows you to create
        DXF files for applications that handles file encoding different than AutoCAD.

        Args:
            filename: file name as string
            encoding: override default encoding as Python encoding string like ``'utf-8'``
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for Binary DXF

        """
        self.filename = filename
        self.save(encoding=encoding, fmt=fmt)

    def save(self, encoding: str = None, fmt: str = 'asc') -> None:
        """
        Write drawing to file-system by using the :attr:`filename` attribute as filename.
        Override file encoding by argument `encoding`, handle with care, but this option allows you to create
        DXF files for applications that handles file encoding different than AutoCAD.

        Args:
            encoding: override default encoding as Python encoding string like ``'utf-8'``
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for Binary DXF
        """
        # DXF R12, R2000, R2004 - ASCII encoding
        # DXF R2007 and newer - UTF-8 encoding
        # in ASCII mode, unknown characters will be escaped as \U+nnnn unicode characters.

        if encoding is None:
            enc = self.output_encoding
        else:  # override default encoding, for applications that handle encoding different than AutoCAD
            enc = encoding

        if fmt.startswith('asc'):
            fp = io.open(self.filename, mode='wt', encoding=enc, errors='dxfreplace')
        elif fmt.startswith('bin'):
            fp = open(self.filename, 'wb')
        else:
            raise ValueError(f"Unknown output format: '{fmt}'.")
        try:
            self.write(fp, fmt=fmt)
        finally:
            fp.close()

    def write(self, stream: Union[TextIO, BinaryIO], fmt: str = 'asc') -> None:
        """
        Write drawing as ASCII DXF to a text stream or as Binary DXF to a binary stream.
        For DXF R2004 (AC1018) and prior open stream with drawing :attr:`encoding` and :code:`mode='wt'`.
        For DXF R2007 (AC1021) and later use :code:`encoding='utf-8'`, or better use the later added :class:`Drawing`
        property :attr:`output_encoding` which returns the correct encoding automatically.

        Args:
            stream: output text stream or binary stream
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for binary DXF
        """
        dxfversion = self.dxfversion
        if dxfversion == DXF12:
            handles = bool(self.header.get('$HANDLING', 0))
        else:
            handles = True
        if dxfversion > DXF12:
            self.classes.add_required_classes(dxfversion)

        self._create_appids()
        self._update_header_vars()
        self._update_metadata()

        if fmt.startswith('asc'):
            tagwriter = TagWriter(stream, write_handles=handles, dxfversion=dxfversion)
        elif fmt.startswith('bin'):
            tagwriter = BinaryTagWriter(
                stream, write_handles=handles, dxfversion=dxfversion, encoding=self.output_encoding,
            )
            tagwriter.write_signature()
        else:
            raise ValueError(f"Unknown output format: '{fmt}'.")

        self.export_sections(tagwriter)

    def encode_base64(self) -> bytes:
        """ Returns DXF document as base64 encoded binary data.

        .. versionadded:: 0.12
            Thanks to Joseph Flack

        """
        stream = io.StringIO()
        self.write(stream)
        # create binary data with windows line ending
        binary_data = stream.getvalue().encode(self.output_encoding).replace(b'\n', b'\r\n')
        return base64.encodebytes(binary_data)

    def export_sections(self, tagwriter: 'TagWriter') -> None:
        """ DXF export sections. (internal API) """
        dxfversion = tagwriter.dxfversion
        self.header.export_dxf(tagwriter)
        if dxfversion > DXF12:
            self.classes.export_dxf(tagwriter)
        self.tables.export_dxf(tagwriter)
        self.blocks.export_dxf(tagwriter)
        self.entities.export_dxf(tagwriter)
        if dxfversion > DXF12:
            self.objects.export_dxf(tagwriter)
        if self.acdsdata.is_valid:
            self.acdsdata.export_dxf(tagwriter)
        for section in self.stored_sections:
            section.export_dxf(tagwriter)

        tagwriter.write_tag2(0, 'EOF')

    def _update_header_vars(self):
        from ezdxf.lldxf.const import acad_maint_ver

        # set or correct $CMATERIAL handle
        material = self.entitydb.get(self.header.get('$CMATERIAL', None))
        if material is None or material.dxftype() != 'MATERIAL':
            if 'ByLayer' in self.materials:
                self.header['$CMATERIAL'] = self.materials.get('ByLayer').dxf.handle
            else:  # set any handle, except '0' which crashes BricsCAD
                self.header['$CMATERIAL'] = '45'

        # set ACAD maintenance version - same values as used by BricsCAD
        self.header['$ACADMAINTVER'] = acad_maint_ver.get(self.dxfversion, 0)

    def _update_metadata(self):
        if options.write_fixed_meta_data_for_testing:
            fixed_date = juliandate(datetime(2000, 1, 1, 0, 0))
            self.header['$TDCREATE'] = fixed_date
            self.header['$TDUCREATE'] = fixed_date
            self.header['$TDUPDATE'] = fixed_date
            self.header['$TDUUPDATE'] = fixed_date
            self.header['$VERSIONGUID'] = '00000000-0000-0000-0000-000000000000'
            self.header['$FINGERPRINTGUID'] = '00000000-0000-0000-0000-000000000000'
        else:
            now = datetime.now()
            self.header['$TDUPDATE'] = juliandate(now)
            self.reset_version_guid()

        self.header['$HANDSEED'] = str(self.entitydb.handles)  # next handle
        self.header['$DWGCODEPAGE'] = tocodepage(self.encoding)

    def _create_appid_if_not_exist(self, name: str, flags: int = 0) -> None:
        if name not in self.appids:
            self.appids.new(name, {'flags': flags})

    def _create_appids(self):
        if 'HATCH' in self.tracker.dxftypes:
            self._create_appid_if_not_exist('HATCHBACKGROUNDCOLOR', 0)

    @property
    def acad_release(self) -> str:
        """ Returns the AutoCAD release number like ``'R12'`` or ``'R2000'``. """
        return acad_release.get(self.dxfversion, "unknown")

    @property
    def layers(self) -> 'Table':
        return self.tables.layers

    @property
    def linetypes(self) -> 'Table':
        return self.tables.linetypes

    @property
    def styles(self) -> 'Table':
        return self.tables.styles

    @property
    def dimstyles(self) -> 'Table':
        return self.tables.dimstyles

    @property
    def ucs(self) -> 'Table':
        return self.tables.ucs

    @property
    def appids(self) -> 'Table':
        return self.tables.appids

    @property
    def views(self) -> 'Table':
        return self.tables.views

    @property
    def block_records(self) -> 'Table':
        return self.tables.block_records

    @property
    def viewports(self) -> 'ViewportTable':
        return self.tables.viewports

    @property
    def plotstyles(self) -> 'Dictionary':
        return self.rootdict['ACAD_PLOTSTYLENAME']

    @property
    def dimension_renderer(self) -> DimensionRenderer:
        return self._dimension_renderer

    @dimension_renderer.setter
    def dimension_renderer(self, renderer: DimensionRenderer) -> None:
        """
        Set your own dimension line renderer if needed.

        see also: ezdxf.render.dimension

        """
        self._dimension_renderer = renderer

    def modelspace(self) -> 'Layout':
        """ Returns the modelspace layout, displayed as ``'Model'`` tab in CAD applications, defined by block record
        named ``'*Model_Space'``.
        """
        return self.layouts.modelspace()

    def layout(self, name: str = None) -> 'Layout':
        """ Returns paperspace layout `name` or returns first layout in tab order if `name` is ``None``. """
        return self.layouts.get(name)

    def active_layout(self) -> 'Layout':
        """ Returns the active paperspace layout, defined by block record name ``'*Paper_Space'``. """
        return self.layouts.active_layout()

    def layout_names(self) -> Iterable[str]:
        """ Returns all layout names (modelspace ``'Model'`` included) in arbitrary order. """
        return list(self.layouts.names())

    def layout_names_in_taborder(self) -> Iterable[str]:
        """ Returns all layout names (modelspace included, always first name) in tab order. """
        return list(self.layouts.names_in_taborder())

    def reset_fingerprint_guid(self):
        """ Reset fingerprint GUID. """
        self.header['$FINGERPRINTGUID'] = guid()

    def reset_version_guid(self):
        """ Reset version GUID. """
        self.header['$VERSIONGUID'] = guid()

    @property
    def acad_compatible(self) -> bool:
        """ Returns ``True`` if drawing is AutoCAD compatible. """
        return self._acad_compatible

    def add_acad_incompatibility_message(self, msg: str):
        """ Add AutoCAD incompatibility message. (internal API) """
        self._acad_compatible = False
        if msg not in self._acad_incompatibility_reason:
            self._acad_incompatibility_reason.add(msg)
            logger.warning(f'Drawing is incompatible to AutoCAD, because {msg}.')

    def query(self, query: str = '*') -> EntityQuery:
        """
        Entity query over all layouts and blocks, excluding the OBJECTS section.

        Args:
            query: query string

        .. seealso::

            :ref:`entity query string` and :ref:`entity queries`

        """
        return EntityQuery(self.chain_layouts_and_blocks(), query)

    def groupby(self, dxfattrib="", key=None) -> dict:
        """
        Groups DXF entities of all layouts and blocks (excluding the OBJECTS section) by a DXF attribute or a key
        function.

        Args:
            dxfattrib: grouping DXF attribute like ``'layer'``
            key: key function, which accepts a :class:`DXFEntity` as argument and returns a hashable grouping key
                 or ``None`` to ignore this entity.

        .. seealso::

            :func:`~ezdxf.groupby.groupby` documentation

        """
        return groupby(self.chain_layouts_and_blocks(), dxfattrib, key)

    def chain_layouts_and_blocks(self) -> Iterable['DXFEntity']:
        """
        Chain entity spaces of all layouts and blocks. Yields an iterator for all entities in all layouts and blocks.

        """
        layouts = list(self.layouts_and_blocks())
        return chain.from_iterable(layouts)

    def layouts_and_blocks(self) -> Iterable['LayoutType']:
        """
        Iterate over all layouts (modelspace and paperspace) and all block definitions.

        """
        return iter(self.blocks)

    def delete_layout(self, name: str) -> None:
        """
        Delete paper space layout `name` and all entities owned by this layout. Available only for DXF R2000 or later,
        DXF R12 supports only one paperspace and it can't be deleted.

        """
        if name not in self.layouts:
            raise DXFValueError(f"Layout '{name}' does not exist.")
        else:
            self.layouts.delete(name)

    def new_layout(self, name, dxfattribs=None) -> 'Layout':
        """
        Create a new paperspace layout `name`. Returns a :class:`~ezdxf.layouts.Layout` object.
        DXF R12 (AC1009) supports only one paperspace layout, only the active paperspace layout is saved, other layouts
        are dismissed.

        Args:
            name: unique layout name
            dxfattribs: additional DXF attributes for the :class:`~ezdxf.entities.layout.DXFLayout` entity

        Raises:
            DXFValueError: :class:`~ezdxf.layouts.Layout` `name` already exist

        """
        if name in self.layouts:
            raise DXFValueError(f"Layout '{name}' already exists.")
        else:
            return self.layouts.new(name, dxfattribs)

    def acquire_arrow(self, name: str):
        """
        For standard AutoCAD and ezdxf arrows create block definitions if required, otherwise check if block `name`
        exist. (internal API)

        """
        from ezdxf.render.arrows import ARROWS
        if ARROWS.is_acad_arrow(name) or ARROWS.is_ezdxf_arrow(name):
            ARROWS.create_block(self.blocks, name)
        elif name not in self.blocks:
            raise DXFValueError(f'Arrow block "{name}" does not exist.')

    def add_image_def(self, filename: str, size_in_pixel: Tuple[int, int], name=None):
        """
        Add an image definition to the objects section.

        Add an :class:`~ezdxf.entities.image.ImageDef` entity to the drawing (objects section). `filename` is the image
        file name as relative or absolute path and `size_in_pixel` is the image size in pixel as (x, y) tuple. To avoid
        dependencies to external packages, `ezdxf` can not determine the image size by itself. Returns a
        :class:`~ezdxf.entities.image.ImageDef` entity which is needed to create an image reference. `name` is the
        internal image name, if set to ``None``, name is auto-generated.

        Absolute image paths works best for AutoCAD but not really good, you have to update external references manually
        in AutoCAD, which is not possible in TrueView. If the drawing units differ from 1 meter, you also have to use:
        :meth:`set_raster_variables`.

        Args:
            filename: image file name (absolute path works best for AutoCAD)
            size_in_pixel: image size in pixel as (x, y) tuple
            name: image name for internal use, None for using filename as name (best for AutoCAD)

        .. seealso::

            :ref:`tut_image`

        """
        if 'ACAD_IMAGE_VARS' not in self.rootdict:
            self.objects.set_raster_variables(frame=0, quality=1, units='m')
        if name is None:
            name = filename
        return self.objects.add_image_def(filename, size_in_pixel, name)

    def set_raster_variables(self, frame: int = 0, quality: int = 1, units: str = 'm'):
        """
        Set raster variables.

        Args:
            frame: ``0`` = do not show image frame; ``1`` = show image frame
            quality: ``0`` = draft; ``1`` = high
            units: units for inserting images. This defines the real world unit for one drawing unit for the purpose of
                   inserting and scaling images with an associated resolution.

                   ===== ===========================
                   mm    Millimeter
                   cm    Centimeter
                   m     Meter (ezdxf default)
                   km    Kilometer
                   in    Inch
                   ft    Foot
                   yd    Yard
                   mi    Mile
                   ===== ===========================

        """
        self.objects.set_raster_variables(frame=frame, quality=quality, units=units)

    def set_wipeout_variables(self, frame=0):
        """
        Set wipeout variables.

        Args:
            frame: ``0`` = do not show image frame; ``1`` = show image frame

        """
        self.objects.set_wipeout_variables(frame=frame)
        var_dict = self.rootdict.get_required_dict('AcDbVariableDictionary')
        var_dict.set_or_add_dict_var('WIPEOUTFRAME', str(frame))

    def add_underlay_def(self, filename: str, format: str = 'ext', name: str = None):
        """
        Add an :class:`~ezdxf.entities.underlay.UnderlayDef` entity to the drawing (OBJECTS section).
        `filename` is the underlay file name as relative or absolute path and `format` as string (pdf, dwf, dgn).
        The underlay definition is required to create an underlay reference.

        Args:
            filename: underlay file name
            format: file format as string ``'pdf'|'dwf'|'dgn'`` or ``'ext'`` for getting file format from filename extension
            name: pdf format = page number to display; dgn format = ``'default'``; dwf: ????

        .. seealso::

            :ref:`tut_underlay`

        """
        if format == 'ext':
            format = filename[-3:]
        return self.objects.add_underlay_def(filename, format, name)

    def add_xref_def(self, filename: str, name: str, flags: int = BLK_XREF | BLK_EXTERNAL):
        """
        Add an external reference (xref) definition to the blocks section.

        Args:
            filename: external reference filename
            name: name of the xref block
            flags: block flags

        """
        self.blocks.new(name=name, dxfattribs={
            'flags': flags,
            'xref_path': filename
        })

    def audit(self) -> 'Auditor':
        """
        Checks document integrity and fixes all fixable problems, not fixable problems are stored in
        :attr:`Auditor.errors`.

        If you are messing around with internal structures, call this method before saving to be sure to export valid
        DXF documents, but be aware this is a long running task.

        """
        from ezdxf.audit.auditor import Auditor
        auditor = Auditor(self)
        auditor.run()
        return auditor

    def validate(self, print_report=True) -> bool:
        """
        Simple way to run an audit process. Fixes all fixable problems, return ``False`` if not fixable errors
        occurs, to get more information about not fixable errors use :meth:`audit` method instead.

        Args:
            print_report: print report to stdout

        Returns: ``True`` if no errors occurred

        """
        auditor = self.audit()
        if len(auditor):
            if print_report:
                auditor.print_error_report()
            return False
        else:
            return True

    def set_modelspace_vport(self, height, center=(0, 0)) -> 'VPort':
        """ Set initial view/zoom location for the modelspace, this replaces the actual
        ``'*Active'`` viewport configuration.

        Args:
             height: modelspace area to view
             center: modelspace location to view in the center of the CAD application window.

        .. versionadded:: 0.11

        """
        self.viewports.delete_config('*Active')
        vport = cast('VPort', self.viewports.new('*Active'))
        vport.dxf.center = center
        vport.dxf.height = height
        return vport
