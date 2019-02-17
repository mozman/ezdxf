# Created: 11.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, TextIO, Iterable
from datetime import datetime
import io
import logging
from itertools import chain

from ezdxf.lldxf.const import DXFVersionError, acad_release, BLK_XREF, BLK_EXTERNAL, DXFValueError
from ezdxf.lldxf.const import DXF12, DXF13, DXF14, DXF2000, LATEST_DXF_VERSION
from ezdxf.lldxf.loader import load_dxf_structure, fill_database2
from ezdxf.lldxf import repair

from ezdxf.entitydb import EntityDB
from ezdxf.entities.factory import EntityFactory
from ezdxf.entities.layouts import Layouts
from ezdxf.templates import TemplateLoader
from ezdxf.options import options
from ezdxf.tools.codepage import tocodepage, toencoding
from ezdxf.sections.sections2 import Sections
from ezdxf.tools.juliandate import juliandate

from ezdxf.tools import guid
from ezdxf.tracker import Tracker
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.render.dimension import DimensionRenderer

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from .eztypes import HandleGenerator, DXFTag, LayoutType, SectionDict
    from .eztypes import GroupManager, MaterialManager, MLeaderStyleManager, MLineStyleManager
    from .eztypes import SectionType,  Table, ViewportTable
    from ezdxf.sections.header import HeaderSection
    from ezdxf.sections.blocks2 import BlocksSection


class Drawing:
    def __init__(self):
        self.entitydb = EntityDB()
        self.dxffactory = EntityFactory(self)
        self.tracker = Tracker()
        self.dxfversion = LATEST_DXF_VERSION
        self.encoding = 'ANSI_1252'
        self.filename = None  # type: str # read/write
        self._groups = None  # type: GroupManager  # read only
        self._materials = None  # type: MaterialManager # read only
        self._mleader_styles = None  # type: MLeaderStyleManager # read only
        self._mline_styles = None  # type: MLineStyleManager # read only
        self._acad_compatible = True  # will generated DXF file compatible with AutoCAD
        self._dimension_renderer = DimensionRenderer()  # set DIMENSION rendering engine
        self._acad_incompatibility_reason = set()  # avoid multiple warnings for same reason

        self.sections = Sections(self)
        # self.rootdict = self.objects.rootdict
        # self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables
        # self._groups = self.objects.groups()
        # self._materials = self.objects.materials()
        # self._mleader_styles = self.objects.mleader_styles()
        # self._mline_styles = self.objects.mline_styles()

        # self.layouts = Layouts(self)


    @property
    def header(self) -> 'HeaderSection':
        return self.sections.header

    @property
    def blocks(self) -> 'BlocksSection':
        return self.sections.blocks

    @property
    def entities(self):
        return self.sections.entities

    @property
    def objects(self):
        return self.sections.objects

    @property
    def layers(self) -> 'Table':
        return self.sections.tables.layers

    @property
    def linetypes(self) -> 'Table':
        return self.sections.tables.linetypes

    @property
    def styles(self) -> 'Table':
        return self.sections.tables.styles

    @property
    def dimstyles(self) -> 'Table':
        return self.sections.tables.dimstyles

    @property
    def ucs(self) -> 'Table':
        return self.sections.tables.ucs

    @property
    def appids(self) -> 'Table':
        return self.sections.tables.appids

    @property
    def views(self) -> 'Table':
        return self.sections.tables.views

    @property
    def block_records(self) -> 'Table':
        return self.sections.tables.block_records

    @property
    def viewports(self) -> 'ViewportTable':
        return self.sections.tables.viewports


    @property
    def groups(self) -> 'GroupManager':
        if self.dxfversion <= 'AC1009':
            raise DXFVersionError('Groups not supported in DXF version R12.')
        return self._groups

    @property
    def materials(self) -> 'MaterialManager':
        if self.dxfversion <= 'AC1009':
            raise DXFVersionError('Materials not supported in DXF version R12.')
        return self._materials

    @property
    def mleader_styles(self) -> 'MLeaderStyleManager':
        if self.dxfversion <= 'AC1009':
            raise DXFVersionError('MLeaderStyles not supported in DXF version R12.')
        return self._mleader_styles

    @property
    def mline_styles(self) -> 'MLineStyleManager':
        if self.dxfversion <= 'AC1009':
            raise DXFVersionError('MLineStyles not supported in DXF version R12.')
        return self._mline_styles

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

    @classmethod
    def new(cls) -> 'Drawing':
        doc = cls()
        doc.setup_metadata()
        return doc

    def setup_metadata(self):
        self.header['$TDCREATE'] = juliandate(datetime.now())

    @classmethod
    def load(self)->'Drawing':
        pass

    @classmethod
    def read(cls, stream: TextIO, legacy_mode: bool = False) -> 'Drawing':
        """ Open an existing drawing. """
        from .lldxf.tagger import low_level_tagger, tag_compiler

        tagger = low_level_tagger(stream)
        if legacy_mode:
            tagger = repair.tag_reorder_layer(tagger)
        tagreader = tag_compiler(tagger)
        doc = Drawing()
        doc.load_tags(tagreader)
        return doc

    def load_tags(self, tagger: Iterable['DXFTag'])->'Drawing':
        def get_header(sections: 'SectionDict') -> 'SectionType':
            from .sections.header import HeaderSection
            header_entities = sections.get('HEADER', [None])[0]  # all tags in the first DXF structure entity
            return HeaderSection.load(header_entities)

        sections = load_dxf_structure(tagger)  # load complete DXF entity structure
        # create section HEADER
        header = get_header(sections)
        self.dxfversion = header.get('$ACADVER', LATEST_DXF_VERSION)  # type: str # read only
        self.encoding = toencoding(header.get('$DWGCODEPAGE', 'ANSI_1252'))  # type: str # read/write
        # get handle seed
        seed = header.get('$HANDSEED', str(self.entitydb.handles))  # type: str
        # setup handles
        self.entitydb.handles.reset(seed)
        # store all necessary DXF entities in the drawing database
        fill_database2(sections, self.dxffactory)
        # create sections: TABLES, BLOCKS, ENTITIES, CLASSES, OBJECTS
        self.sections = Sections(sections, drawing=self, header=header)
        self.rootdict = self.objects.rootdict
        self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables
        if self.dxfversion in (DXF13, DXF14):
            repair.upgrade_to_ac1015(self)
        # some applications don't setup properly the model and paper space layouts
        repair.setup_layouts(self)
        self._groups = self.objects.groups()
        self._materials = self.objects.materials()
        self._mleader_styles = self.objects.mleader_styles()
        self._mline_styles = self.objects.mline_styles()
        self.layouts = Layouts(self)


class DrawingX(Drawing):
    """
    The Central Data Object
    """

    def __init__(self, tagger: Iterable['DXFTag']):
        """
        Build a new DXF drawing from a steam of DXF tags.

        Args:
             tagger: generator or list of DXF tags as DXFTag() objects
        """
        super().__init__()

        def get_header(sections: 'SectionDict') -> 'SectionType':
            from .sections.header import HeaderSection
            header_entities = sections.get('HEADER', [None])[0]  # all tags in the first DXF structure entity
            return HeaderSection.load(header_entities)

        self._dimension_renderer = DimensionRenderer()  # set DIMENSION rendering engine
        self._acad_incompatibility_reason = set()  # avoid multiple warnings for same reason

        sections = load_dxf_structure(tagger)  # load complete DXF entity structure
        # create section HEADER
        header = get_header(sections)
        self.dxfversion = header.get('$ACADVER', DXF12)  # type: str # read only

        self.encoding = toencoding(header.get('$DWGCODEPAGE', 'ANSI_1252'))  # type: str # read/write
        # get handle seed
        seed = header.get('$HANDSEED', str(self.entitydb.handles))  # type: str
        # setup handles
        self.entitydb.handles.reset(seed)
        # store all necessary DXF entities in the drawing database
        fill_database2(sections, self.dxffactory)
        # create sections: TABLES, BLOCKS, ENTITIES, CLASSES, OBJECTS
        self.sections = Sections(sections, drawing=self, header=header)

        if self.dxfversion <= DXF12:
            self.setup_r12()

        self.rootdict = self.objects.rootdict
        self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables
        if self.dxfversion in (DXF13, DXF14):
            repair.upgrade_to_ac1015(self)
        # some applications don't setup properly the model and paper space layouts
        repair.setup_layouts(self)
        self._groups = self.objects.groups()
        self._materials = self.objects.materials()
        self._mleader_styles = self.objects.mleader_styles()
        self._mline_styles = self.objects.mline_styles()
        self.layouts = Layouts(self)

    def setup_r12(self):
        # create:
        # objects section
        # root dict

        if self.dxfversion < DXF12:  # legacy DXF version
            self.header['$ACADVER'] = DXF12  # upgrade to DXF format AC1009 (DXF R12)

        # ezdxf puts automatically handles into all entities added to the entities database
        # write R12 without handles, by setting $HANDLING = 0
        self.header['$HANDLING'] = 1  # write handles by default

    @property
    def is_loaded(self):
        return hasattr(self, 'section')

    @property
    def acad_release(self) -> str:
        return acad_release.get(self.dxfversion, "unknown")

    @property
    def acad_compatible(self) -> bool:
        return self._acad_compatible

    def add_acad_incompatibility_message(self, msg: str):
        self._acad_compatible = False
        if msg not in self._acad_incompatibility_reason:
            self._acad_incompatibility_reason.add(msg)
            logger.warning('Drawing is incompatible to AutoCAD, because {}.'.format(msg))

    @property
    def _handles(self) -> 'HandleGenerator':
        return self.entitydb.handles


    def modelspace(self) -> 'LayoutType':
        return self.layouts.modelspace()

    def layout(self, name: str = None) -> 'LayoutType':
        return self.layouts.get(name)

    def layout_names(self) -> Iterable[str]:
        return list(self.layouts.names())

    def delete_layout(self, name):
        if self.dxfversion > 'AC1009':
            if name not in self.layouts:
                raise DXFValueError("Layout '{}' does not exist.".format(name))
            else:
                self.layouts.delete(name)
        else:
            raise DXFVersionError('delete_layout() not supported for DXF version R12.')

    def new_layout(self, name, dxfattribs=None):
        if self.dxfversion > 'AC1009':
            if name in self.layouts:
                raise DXFValueError("Layout '{}' already exists.".format(name))
            else:
                return self.layouts.new(name, dxfattribs)
        else:
            raise DXFVersionError('new_layout() not supported for DXF version R12.')

    def layouts_and_blocks(self):
        """
        Iterate over all layouts (mode space and paper space) and all block definitions.

        Returns: yields Layout() objects

        """
        # DXF R12: model space and paper space layouts not linked into the associated BLOCK entity
        if self.dxfversion <= 'AC1009':
            return chain(self.layouts, self.blocks)
        # DXF R2000+: all layout spaces linked into their associated BLOCK entity
        else:
            return iter(self.blocks)

    def chain_layouts_and_blocks(self):
        """
        Chain entity spaces of all layouts and blocks. Yields an iterator for all entities in all layouts and blocks.

        Returns: yields all entities as DXFEntity() objects

        """
        layouts = list(self.layouts_and_blocks())
        return chain.from_iterable(layouts)

    def get_active_layout_key(self):
        if self.dxfversion > 'AC1009':
            try:
                active_layout_block_record = self.block_records.get('*Paper_Space')  # block names are case insensitive
                return active_layout_block_record.dxf.handle
            except DXFValueError:
                return None
        else:
            return self.layout().layout_key  # AC1009 supports just one layout and this is the active one

    def get_active_entity_space_layout_keys(self):
        layout_keys = [self.modelspace().layout_key]
        active_layout_key = self.get_active_layout_key()
        if active_layout_key is not None:
            layout_keys.append(active_layout_key)
        return layout_keys


    def get_dxf_entity(self, handle):
        """
        Get entity by *handle* from entity database.

        Low level access to DXF entities database. Raises *KeyError* if handle don't exists.
        Returns DXFEntity() or inherited.

        If you just need the raw DXF tags use::

            tags = Drawing.entitydb[handle]  # raises KeyError, if handle don't exist
            tags = Drawing.entitydb.get(handle)  # returns a default value, if handle don't exist (None by default)

        type of tags: ExtendedTags()
        """
        return self.dxffactory.wrap_handle(handle)

    def add_image_def(self, filename, size_in_pixel, name=None):
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
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('The IMAGE entity needs at least DXF version R2000 or later.')

        if 'ACAD_IMAGE_VARS' not in self.rootdict:
            self.objects.set_raster_variables(frame=0, quality=1, units=3)
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

    def add_underlay_def(self, filename, format='ext', name=None):
        """
        Add an underlay definition to the objects section.

        Args:
            format: file format as string pdf|dwf|dgn or ext=get format from filename extension
            name: underlay name, None for an auto-generated name

        """
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('The UNDERLAY entity needs at least DXF version R2000 or later.')
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

    def _get_encoding(self):
        codepage = self.header.get('$DWGCODEPAGE', 'ANSI_1252')
        return toencoding(codepage)

    @staticmethod
    def new(dxfversion='AC1009'):
        from .lldxf.const import versions_supported_by_new, acad_release_to_dxf_version

        dxfversion = dxfversion.upper()
        dxfversion = acad_release_to_dxf_version.get(dxfversion, dxfversion)  # translates 'R12' -> 'AC1009'
        if dxfversion not in versions_supported_by_new:
            raise DXFVersionError("Can not create DXF drawings, unsupported DXF version '{}'.".format(dxfversion))
        finder = TemplateLoader(options.template_dir)
        stream = finder.getstream(dxfversion.upper())
        try:
            dwg = Drawing.read(stream)
        finally:
            stream.close()
        dwg._setup_metadata()
        return dwg

    def _setup_metadata(self):
        self.header['$TDCREATE'] = juliandate(datetime.now())

    @staticmethod
    def read(stream: TextIO, legacy_mode: bool = False, dxfversion: str = None) -> 'Drawing':
        """ Open an existing drawing. """
        from .lldxf.tagger import low_level_tagger, tag_compiler

        tagger = low_level_tagger(stream)
        if legacy_mode:
            if dxfversion is not None and dxfversion <= 'AC1009':
                tagger = repair.filter_subclass_marker(tagger)
            tagger = repair.tag_reorder_layer(tagger)
        tagreader = tag_compiler(tagger)
        return Drawing(tagreader)

    def saveas(self, filename, encoding=None):
        self.filename = filename
        self.save(encoding=encoding)

    def save(self, encoding=None):
        # DXF R12, R2000, R2004 - ASCII encoding
        # DXF R2007 and newer - UTF-8 encoding
        if encoding is None:
            enc = 'utf-8' if self.dxfversion >= 'AC1021' else self.encoding
        else:  # override default encoding, for applications that handles encoding different than AutoCAD
            enc = encoding
        # in ASCII mode, unknown characters will be escaped as \U+nnnn unicode characters.
        with io.open(self.filename, mode='wt', encoding=enc, errors='dxfreplace') as fp:
            self.write(fp)

    def write(self, stream):
        from .lldxf.tagwriter import TagWriter
        if self.dxfversion == 'AC1009':
            handles = bool(self.header['$HANDLING'])
        else:
            handles = True
        if self.dxfversion > 'AC1009':
            self._register_required_classes()
            if self.dxfversion < 'AC1018':
                # remove unsupported group code 91
                repair.fix_classes(self)

        self._create_appids()
        self._update_metadata()
        tagwriter = TagWriter(stream, write_handles=handles)
        self.sections.write(tagwriter)

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

    def update_class_instance_counters(self):
        if 'classes' in self.sections:
            self._register_required_classes()
            self.sections.classes.update_instance_counters()

    def _register_required_classes(self):
        register = self.sections.classes.register
        for dxftype in self.tracker.dxftypes:
            cls = self.dxffactory.get_wrapper_class(dxftype)
            if cls.CLASS is not None:
                register(cls.CLASS)

    def _update_metadata(self):
        now = datetime.now()
        self.header['$TDUPDATE'] = juliandate(now)
        self.header['$HANDSEED'] = str(self.entitydb.handles)
        self.header['$DWGCODEPAGE'] = tocodepage(self.encoding)
        self.reset_versionguid()

    def _create_appids(self):
        def create_appid_if_not_exist(name, flags=0):
            if name not in self.appids:
                self.appids.new(name, {'flags': flags})

        if 'HATCH' in self.tracker.dxftypes:
            create_appid_if_not_exist('HATCHBACKGROUNDCOLOR', 0)

    def reset_fingerprintguid(self):
        if self.dxfversion > 'AC1009':
            self.header['$FINGERPRINTGUID'] = guid()

    def reset_versionguid(self):
        if self.dxfversion > 'AC1009':
            self.header['$VERSIONGUID'] = guid()
