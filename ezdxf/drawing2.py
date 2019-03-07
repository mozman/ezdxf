# Created: 11.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, TextIO, Iterable, Union, Sequence, Tuple, Callable
from datetime import datetime
import io
import logging
from itertools import chain

from ezdxf.lldxf.const import acad_release, BLK_XREF, BLK_EXTERNAL, DXFValueError, acad_release_to_dxf_version
from ezdxf.lldxf.const import DXF13, DXF14, DXF2000, DXF2007, DXF12, DXF2013, versions_supported_by_save
from ezdxf.lldxf.const import DXFVersionError
from ezdxf.lldxf.loader import load_dxf_structure, fill_database2
from ezdxf.lldxf import repair
from .lldxf.tagwriter import TagWriter

from ezdxf.entitydb import EntityDB
from ezdxf.entities.factory import EntityFactory
from ezdxf.layouts.layouts import Layouts
from ezdxf.tools.codepage import tocodepage, toencoding
from ezdxf.tools.juliandate import juliandate

from ezdxf.tools import guid
from ezdxf.tracker import Tracker
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.render.dimension import DimensionRenderer

from ezdxf.sections.header import HeaderSection
from ezdxf.sections.classes2 import ClassesSection
from ezdxf.sections.tables2 import TablesSection
from ezdxf.sections.blocks2 import BlocksSection
from ezdxf.sections.entities2 import EntitySection, StoredSection
from ezdxf.sections.objects2 import ObjectsSection

from ezdxf.entities.dxfgroups import GroupCollection
from ezdxf.entities.material import MaterialCollection
from ezdxf.entities.mleader import MLeaderStyleCollection
from ezdxf.entities.mline import MLineStyleCollection

logger = logging.getLogger('ezdxf')
MANAGED_SECTIONS = {'HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS'}

if TYPE_CHECKING:
    from ezdxf.eztypes2 import HandleGenerator, DXFTag, SectionDict, SectionType, Table, ViewportTable
    from ezdxf.eztypes2 import Dictionary, BlockLayout, Layout
    from ezdxf.eztypes2 import DXFEntity, Layer, DXFLayout, BlockRecord

    LayoutType = Union[Layout, BlockLayout]

TFilterStack = Sequence[Sequence[Callable[[Iterable['DXFTag']], Iterable['DXFTag']]]]


# [(raw_tag_filter1, raw_tag_filter2), (compiled_tag_filter1, )]

class Drawing:
    def __init__(self, dxfversion=DXF2013):
        self.entitydb = EntityDB()
        self.dxffactory = EntityFactory(self)
        self.tracker = Tracker()  # still required

        # Targeted DXF version, but drawing could be exported as another DXF version.
        # If target version is set, it is possible to warn user, if they try to use unsupported features, where they
        # use it and not at exporting, where the location of the code who created that features is not known.
        target_dxfversion = dxfversion.upper()
        self._dxfversion = acad_release_to_dxf_version.get(target_dxfversion, target_dxfversion)
        self._loaded_dxfversion = None  # if loaded from file, store original dxf version
        self.encoding = 'cp1252'
        self.filename = None  # type: str # read/write

        # named objects dictionary
        self.rootdict = None  # type: Dictionary

        # DXF sections
        self.header = None  # type: HeaderSection
        self.classes = None  # type: ClassesSection
        self.tables = None  # type: TablesSection
        self.blocks = None  # type: BlocksSection
        self.entities = None  # type: EntitySection
        self.objects = None  # type: ObjectsSection
        self.stored_sections = []
        self.layouts = None  # type: Layouts
        self.groups = None  # type: GroupCollection  # read only
        self.materials = None  # type: MaterialCollection # read only
        self.mleader_styles = None  # type: MLeaderStyleCollection # read only
        self.mline_styles = None  # type: MLineStyleCollection # read only
        self._acad_compatible = True  # will generated DXF file compatible with AutoCAD
        self._dimension_renderer = DimensionRenderer()  # set DIMENSION rendering engine
        self._acad_incompatibility_reason = set()  # avoid multiple warnings for same reason
        # Don't create any new entities here:
        # New created handles could collide with handles loaded from DXF file.
        assert len(self.entitydb) == 0

    @classmethod
    def new(cls, dxfversion=DXF2013) -> 'Drawing':
        doc = Drawing(dxfversion)
        doc._setup()
        return doc

    def _get_encoding(self):
        codepage = self.header.get('$DWGCODEPAGE', 'ANSI_1252')
        return toencoding(codepage)

    def _setup(self):
        self.header = HeaderSection.new()
        self.classes = ClassesSection(self)
        self.tables = TablesSection(self)
        self.blocks = BlocksSection(self)
        self.entities = EntitySection(self)
        self.objects = ObjectsSection(self)

        self.rootdict = self.objects.rootdict
        self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables
        self.layouts = Layouts.setup(self)
        self._finalize_setup()

    def _finalize_setup(self):
        """ Common setup tasks for new and loaded DXF drawings. """
        self.groups = GroupCollection(self)
        self.materials = MaterialCollection(self)
        self.mleader_styles = MLeaderStyleCollection(self)
        self.mline_styles = MLineStyleCollection(self)
        # all required internal structures are ready
        # now do the stuff to please AutoCAD
        self._create_required_table_entries()
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

    def _setup_metadata(self):
        self.header['$ACADVER'] = self.dxfversion
        self.header['$TDCREATE'] = juliandate(datetime.now())
        self.reset_fingerprintguid()
        self.reset_versionguid()

    @property
    def dxfversion(self) -> str:
        return self._dxfversion

    @dxfversion.setter
    def dxfversion(self, version) -> None:
        self._dxfversion = self._validate_dxf_version(version)
        self.header['$ACADVER'] = version

    def _validate_dxf_version(self, version: str) -> str:
        version = version.upper()
        version = acad_release_to_dxf_version.get(version, version)  # translates 'R12' -> 'AC1009'
        if version not in versions_supported_by_save:
            raise DXFVersionError('Unsupported DXF version "{}".'.format(version))
        if version == DXF12:
            if self._dxfversion > DXF12:
                logger.warning('Downgrade from DXF {} to R12 may create an invalid DXF file.'.format(
                    self.acad_release
                ))
        elif version < self._dxfversion:
            logger.info('Downgrade from DXF {} to {} can cause lost of features.'.format(
                self.acad_release, acad_release[version]
            ))
        return version

    def which_dxfversion(self, dxfversion=None) -> str:
        dxfversion = dxfversion if dxfversion is not None else self.dxfversion
        return acad_release_to_dxf_version.get(dxfversion, dxfversion)

    @classmethod
    def read(cls, stream: TextIO, legacy_mode: bool = False, filter_stack: TFilterStack = None) -> 'Drawing':
        """ Open an existing drawing.

        Args:
             stream: text stream yielding text (unicode) strings by readline()
             legacy_mode: apply some low level filters to correct some quirks allowed in legacy (R12) files
             filter_stack: interface to put filters between reading layers, list of callable filters, for now
                           two levels are supported, after low level tagging (DXFVertex) and after compiling tags to
                           DXFVertex and DXFBinaryTag.

                TFilterStack: Sequence[Sequence[Callable[[Iterable[DXFTag]], Iterable[DXFTag]]]]
                e.g. [(raw_tag_filter1, raw_tag_filter2), (compiled_tag_filter1, )]

        """
        from .lldxf.tagger import low_level_tagger, tag_compiler
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
        tagger = low_level_tagger(stream)

        # apply low level filters
        for _filter in raw_tag_filters:
            tagger = _filter(tagger)

        # compiles vertices and binary tags into DXFVertex() or DXFBinaryTag()
        tagger = tag_compiler(tagger)

        # apply compiled tags filter
        for _filter in compiled_tag_filters:
            tagger = _filter(tagger)

        doc = Drawing()
        doc._load(tagger)
        return doc

    @classmethod
    def from_tags(cls, compiled_tags: Iterable['DXFTag']) -> 'Drawing':
        doc = Drawing()
        doc._load(compiled_tags)
        return doc

    def _load(self, tagger: Iterable['DXFTag']):
        sections = load_dxf_structure(tagger)  # load complete DXF entity structure
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
        self._dxfversion = self.header.get('$ACADVER', DXF12)  # type: str # read only  # no $ACADVER -> DXF R12
        self._loaded_dxfversion = self._dxfversion  # save dxf version of loaded file
        self.encoding = toencoding(self.header.get('$DWGCODEPAGE', 'ANSI_1252'))  # type: str # read/write
        # get handle seed
        seed = self.header.get('$HANDSEED', str(self.entitydb.handles))  # type: str
        # setup handles
        self.entitydb.handles.reset(seed)
        # store all necessary DXF entities in the drawing database
        fill_database2(sections, self.dxffactory)
        # all handles used in the DXF file are known at this point
        # -----------------------------------------------------------------------------------
        # create sections:
        self.classes = ClassesSection(self, sections.get('CLASSES', None))
        self.tables = TablesSection(self, sections.get('TABLES', None))
        # create *Model_space and *Paper_Space BLOCK_RECORDS
        # BlockSection setup takes care about the rest
        self._create_required_block_records()
        # table records available
        self.blocks = BlocksSection(self, sections.get('BLOCKS', None))

        self.entities = EntitySection(self, sections.get('ENTITIES', None))
        self.objects = ObjectsSection(self, sections.get('OBJECTS', None))
        for name, data in sections.items():
            if name not in MANAGED_SECTIONS:
                self.stored_sections.append(StoredSection(data))
        # -----------------------------------------------------------------------------------
        if self.dxfversion < DXF12:
            # upgrade to DXF R12
            logger.info('Upgrading drawing to DXF R12.')
            self.dxfversion = DXF12

        if self.dxfversion == DXF12:
            # TABLE requires in DXF12 no handle and has no owner tag, but DXF R2000+, requires a TABLE with handle
            # and each table entry has an owner tag, pointing to the TABLE entry
            self.tables.create_table_handles()

        if self.dxfversion in (DXF13, DXF14):
            # upgrade to DXF R2000
            # todo: more?
            self.dxfversion = DXF2000

        self.rootdict = self.objects.rootdict
        self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables

        # some applications don't setup properly the model and paper space layouts
        # repair.setup_layouts(self)
        self.layouts = Layouts.load(self)
        self._finalize_setup()

    def _create_required_block_records(self):
        if '*Model_Space' not in self.block_records:
            self.block_records.new('*Model_Space')
        if '*Paper_Space' not in self.block_records:
            self.block_records.new('*Paper_Space')

    def saveas(self, filename, encoding=None, dxfversion=None) -> None:
        dxfversion = self.which_dxfversion(dxfversion)
        self.filename = filename
        self.save(encoding=encoding, dxfversion=dxfversion)

    def save(self, encoding=None, dxfversion=None) -> None:
        # DXF R12, R2000, R2004 - ASCII encoding
        # DXF R2007 and newer - UTF-8 encoding
        dxfversion = self.which_dxfversion(dxfversion)

        if encoding is None:
            enc = 'utf-8' if dxfversion >= DXF2007 else self.encoding
        else:  # override default encoding, for applications that handles encoding different than AutoCAD
            enc = encoding
        # in ASCII mode, unknown characters will be escaped as \U+nnnn unicode characters.

        with io.open(self.filename, mode='wt', encoding=enc, errors='dxfreplace') as fp:
            self.write(fp, dxfversion)

    def write(self, stream, dxfversion=None) -> None:
        dxfversion = self.which_dxfversion(dxfversion)
        dxfversion = self._validate_dxf_version(dxfversion)
        if dxfversion == DXF12:
            handles = bool(self.header.get('$HANDLING', 0))
        else:
            handles = True
        if dxfversion > DXF12:
            self._register_required_classes(dxfversion)

        self._create_appids()
        self._update_metadata()
        tagwriter = TagWriter(stream, write_handles=handles, dxfversion=dxfversion)
        self.export_sections(tagwriter)

    def export_sections(self, tagwriter: 'TagWriter') -> None:
        dxfversion = tagwriter.dxfversion
        self.header.export_dxf(tagwriter)
        if dxfversion > DXF12:
            self.classes.export_dxf(tagwriter)
        self.tables.export_dxf(tagwriter)
        self.blocks.export_dxf(tagwriter)
        self.entities.export_dxf(tagwriter)
        if dxfversion > DXF12:
            self.objects.export_dxf(tagwriter)

        for section in self.stored_sections:
            section.export_dxf(tagwriter)

        tagwriter.write_tag2(0, 'EOF')

    def _register_required_classes(self, dxfversion):
        self.classes.add_required_classes(dxfversion)
        for dxftype in self.tracker.dxftypes:
            self.classes.add_class(dxftype)

    def update_class_instance_counters(self):
        self.classes.update_instance_counters()

    def _update_metadata(self):
        now = datetime.now()
        self.header['$TDUPDATE'] = juliandate(now)
        self.header['$HANDSEED'] = str(self.entitydb.next_handle())
        self.header['$DWGCODEPAGE'] = tocodepage(self.encoding)
        self.reset_versionguid()

    def _create_appids(self):
        def create_appid_if_not_exist(name, flags=0):
            if name not in self.appids:
                self.appids.new(name, {'flags': flags})

        if 'HATCH' in self.tracker.dxftypes:
            create_appid_if_not_exist('HATCHBACKGROUNDCOLOR', 0)

    @property
    def acad_release(self) -> str:
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
        """ Returns the modelspace layout, displayed as 'Model' tab in CAD applications, defined by block record name
        '*Model_Space'.
        """
        return self.layouts.modelspace()

    def layout(self, name: str = None) -> 'Layout':
        """ Returns paperspace layout `name` or returns first layout in tab order if `name` is None. """
        return self.layouts.get(name)

    def active_layout_name(self) -> str:
        """ Returns the active paperspace layout name, name as displayed in tabs of CAD applications, defined by block
        record name '*Paper_Space'
        """
        active_layout_block_record = self.block_records.get(
            '*Paper_Space')  # type: BlockRecord # block names are case insensitive
        dxf_layout = active_layout_block_record.dxf.layout  # type: DXFLayout
        return dxf_layout.dxf.name

    def active_layout(self) -> 'Layout':
        """ Returns the active paperspace layout, defined by block record name '*Paper_Space' """
        return self.layouts.get(self.active_layout_name())

    def layout_names(self) -> Iterable[str]:
        """ Returns all layout names (modelspace included) in arbitrary order. """
        return list(self.layouts.names())

    def layout_names_in_taborder(self) -> Iterable[str]:
        """ Returns all layout names (modelspace included) in tab order. """
        return list(self.layouts.names_in_taborder())

    def reset_fingerprintguid(self):
        self.header['$FINGERPRINTGUID'] = guid()

    def reset_versionguid(self):
        self.header['$VERSIONGUID'] = guid()

    @property
    def acad_compatible(self) -> bool:
        return self._acad_compatible

    def add_acad_incompatibility_message(self, msg: str):
        self._acad_compatible = False
        if msg not in self._acad_incompatibility_reason:
            self._acad_incompatibility_reason.add(msg)
            logger.warning('Drawing is incompatible to AutoCAD, because {}.'.format(msg))

    def query(self, query='*'):
        """
        Entity query over all layouts and blocks.

        Excluding the OBJECTS section!

        Args:
            query: query string

        Returns: EntityQuery() container

        """
        return EntityQuery(self.chain_layouts_and_blocks(), query)

    def groupby(self, dxfattrib="", key=None):
        """
        Groups DXF entities of all layouts and blocks by an DXF attribute or a key function.

        Excluding the OBJECTS section!

        Args:
            dxfattrib: grouping DXF attribute like 'layer'
            key: key function, which accepts a DXFEntity as argument, returns grouping key of this entity or None for ignore
                 this object. Reason for ignoring: a queried DXF attribute is not supported by this entity

        Returns: dict

        """
        return groupby(self.chain_layouts_and_blocks(), dxfattrib, key)

    def chain_layouts_and_blocks(self) -> Iterable['DXFEntity']:
        """
        Chain entity spaces of all layouts and blocks. Yields an iterator for all entities in all layouts and blocks.

        Returns: yields all entities as DXFEntity() objects

        """
        layouts = list(self.layouts_and_blocks())
        return chain.from_iterable(layouts)

    def layouts_and_blocks(self) -> Iterable['LayoutType']:
        """
        Iterate over all layouts (mode space and paper space) and all block definitions.

        Returns: yields Layout() objects

        """
        return iter(self.blocks)

    def delete_layout(self, name):
        if name not in self.layouts:
            raise DXFValueError("Layout '{}' does not exist.".format(name))
        else:
            self.layouts.delete(name)

    def new_layout(self, name, dxfattribs=None):
        if name in self.layouts:
            raise DXFValueError("Layout '{}' already exists.".format(name))
        else:
            return self.layouts.new(name, dxfattribs)

    def add_image_def(self, filename: str, size_in_pixel: Tuple[int, int], name=None):
        """
        Add an image definition to the objects section.

        For AutoCAD works best with absolute image paths but not good, you have to update external references manually
        in AutoCAD, which is not possible in TrueView. If you drawing units differ from 1 meter, you also have to use:
        Drawing.set_raster_variables().

        Args:
            filename: image file name (absolute path works best for AutoCAD)
            size_in_pixel: image size in pixel as (x, y) tuple
            name: image name for internal use, None for using filename as name (best for AutoCAD)

        """

        if 'ACAD_IMAGE_VARS' not in self.rootdict:
            self.objects.set_raster_variables(frame=0, quality=1, units='m')
        if name is None:
            name = filename
        return self.objects.add_image_def(filename, size_in_pixel, name)

    def set_raster_variables(self, frame=0, quality=1, units='m'):
        """
        Set raster variables.

        Args:
            frame: 0 = do not show image frame; 1 = show image frame
            quality: 0 = draft; 1 = high
            units: units for inserting images. This is what one drawing unit is equal to for the purpose of inserting
                   and scaling images with an associated resolution

                   'mm' = Millimeter
                   'cm' = Centimeter
                   'm' = Meter (ezdxf default)
                   'km' = Kilometer
                   'in' = Inch
                   'ft' = Foot
                   'yd' = Yard
                   'mi' = Mile
                   everything else is None

        """
        self.objects.set_raster_variables(frame=frame, quality=quality, units=units)

    def set_wipeout_variables(self, frame=0):
        """
        Set wipeout variables.

        Args:
            frame: 0 = do not show image frame; 1 = show image frame

        """
        self.objects.set_wipeout_variables(frame=frame)

    def add_underlay_def(self, filename: str, format: str = 'ext', name: str = None):
        """
        Add an underlay definition to the objects section.

        Args:
            format: file format as string pdf|dwf|dgn or ext=get format from filename extension
            name: underlay name, None for an auto-generated name

        """
        if format == 'ext':
            format = filename[-3:]
        return self.objects.add_underlay_def(filename, format, name)

    def add_xref_def(self, filename, name, flags=BLK_XREF | BLK_EXTERNAL):
        """
        Add an external reference (xref) definition to the blocks section.

        Add xref to a layout by `layout.add_blockref(name, insert=(0, 0))`.

        Args:
            filename: external reference filename
            name: name of the xref block
            flags: block flags

        """
        self.blocks.new(name=name, dxfattribs={
            'flags': flags,
            'xref_path': filename
        })

    def cleanup(self, groups=True):
        """
        Cleanup drawing. Call it before saving the drawing but only if necessary, the process could take a while.

        Args:
            groups (bool): removes deleted and invalid entities from groups
        """
        if groups and self.groups is not None:
            self.groups.cleanup()

    def auditor(self):
        """
        Get auditor for this drawing.

        Returns:
            Auditor() object

        """
        from ezdxf.audit.auditor import Auditor
        return Auditor(self)

    def validate(self, print_report=True):
        """
        Simple way to run an audit process.

        Args:
            print_report: print report to stdout

        Returns: True if no errors occurred else False

        """
        auditor = self.auditor()
        result = list(auditor.filter_zero_pointers(auditor.run()))
        if len(result):
            if print_report:
                auditor.print_report()
            return False
        else:
            return True
