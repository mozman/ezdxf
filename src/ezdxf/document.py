# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    TextIO,
    BinaryIO,
    Iterable,
    Union,
    Tuple,
    Callable,
    cast,
    Optional,
    List,
    Dict,
)
from datetime import datetime, timezone
import io
import abc
import base64
import logging
from itertools import chain

import ezdxf
from ezdxf.layouts import Modelspace
from ezdxf.lldxf import const
from ezdxf.lldxf.const import (
    BLK_XREF,
    BLK_EXTERNAL,
    DXF13,
    DXF14,
    DXF2000,
    DXF2007,
    DXF12,
    DXF2013,
)
from ezdxf.lldxf import loader
from ezdxf.lldxf.tagwriter import TagWriter, BinaryTagWriter

from ezdxf.entitydb import EntityDB
from ezdxf.layouts.layouts import Layouts
from ezdxf.tools.codepage import tocodepage, toencoding
from ezdxf.tools.juliandate import juliandate
from ezdxf.tools.text import escape_dxf_line_endings

from ezdxf.tools import guid
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

logger = logging.getLogger("ezdxf")

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        DXFTag,
        Table,
        ViewportTable,
        VPort,
        Dictionary,
        Layout,
        DXFEntity,
        Layer,
        Auditor,
        GenericLayoutType,
    )
    from pathlib import Path

CONST_GUID = "{00000000-0000-0000-0000-000000000000}"
CONST_MARKER_STRING = "0.0 @ 2000-01-01T00:00:00.000000+00:00"
CREATED_BY_EZDXF = "CREATED_BY_EZDXF"
WRITTEN_BY_EZDXF = "WRITTEN_BY_EZDXF"
EZDXF_META = "EZDXF_META"


def _validate_handle_seed(seed: str) -> str:
    from ezdxf.tools.handle import START_HANDLE

    if seed is None:
        seed = START_HANDLE
    try:
        v = int(seed, 16)
        if v < 1:
            seed = START_HANDLE
    except ValueError:
        seed = START_HANDLE
    return seed


class Drawing:
    def __init__(self, dxfversion=DXF2013):
        self.entitydb = EntityDB()
        target_dxfversion = dxfversion.upper()
        self._dxfversion: str = const.acad_release_to_dxf_version.get(
            target_dxfversion, target_dxfversion
        )
        if self._dxfversion not in const.versions_supported_by_new:
            raise const.DXFVersionError(
                f'Unsupported DXF version "{self.dxfversion}".'
            )
        # Store original dxf version if loaded (and maybe converted R13/14)
        # from file.
        self._loaded_dxfversion: Optional[str] = None

        # Status flag which is True while loading content from a DXF file:
        self.is_loading = False
        self.encoding: str = "cp1252"  # read/write
        self.filename: Optional[str] = None

        # named objects dictionary
        self.rootdict: "Dictionary" = None

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

        # Set to False if the generated DXF file will be incompatible to AutoCAD
        self._acad_compatible = True
        # Store reasons for AutoCAD incompatibility:
        self._acad_incompatibility_reason = set()

        # DIMENSION rendering engine can be replaced by a custom Dimension
        # render: see property Drawing.dimension_renderer
        self._dimension_renderer = DimensionRenderer()

        # Some fixes can't be applied while the DXF document is not fully
        # initialized, store this fixes as callable object:
        self._post_init_commands: List[Callable] = []
        # Don't create any new entities here:
        # New created handles could collide with handles loaded from DXF file.
        assert len(self.entitydb) == 0

    @classmethod
    def new(cls, dxfversion: str = DXF2013) -> "Drawing":
        """Create new drawing. Package users should use the factory function
        :func:`ezdxf.new`. (internal API)
        """
        doc = cls(dxfversion)
        doc._setup()
        doc._create_ezdxf_metadata()
        return doc

    def _setup(self):
        self.header = HeaderSection.new()
        self.classes = ClassesSection(self)
        self.tables = TablesSection(self)
        self.blocks = BlocksSection(self)
        self.entities = EntitySection(self)
        self.objects = ObjectsSection(self)
        # AcDSData section is not supported for new drawings
        self.acdsdata = AcDsDataSection(self)
        self.rootdict = self.objects.rootdict
        # Create missing tables:
        self.objects.setup_objects_management_tables(self.rootdict)
        self.layouts = Layouts.setup(self)
        self._finalize_setup()

    def _finalize_setup(self):
        """Common setup tasks for new and loaded DXF drawings."""
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
        self._execute_post_init_commands()

    def _execute_post_init_commands(self):
        for cmd in self._post_init_commands:
            cmd()
        del self._post_init_commands

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
        if "*Active" not in self.viewports:
            self.viewports.new("*Active")

    def _create_required_appids(self):
        if "ACAD" not in self.appids:
            self.appids.new("ACAD")

    def _create_required_linetypes(self):
        linetypes = self.linetypes
        for name in ("ByBlock", "ByLayer", "Continuous"):
            if name not in linetypes:
                linetypes.new(name)

    def _create_required_dimstyles(self):
        if "Standard" not in self.dimstyles:
            self.dimstyles.new("Standard")

    def _create_required_styles(self):
        if "Standard" not in self.styles:
            self.styles.new("Standard")

    def _create_required_layers(self):
        layers = self.layers
        if "0" not in layers:
            layers.new("0")
        if "Defpoints" not in layers:
            layers.new("Defpoints", dxfattribs={"plot": 0})  # do not plot
        else:
            # AutoCAD requires a plot flag = 0
            layers.get("Defpoints").dxf.plot = 0

    def _setup_metadata(self):
        self.header["$ACADVER"] = self.dxfversion
        self.header["$TDCREATE"] = juliandate(datetime.now())
        self.reset_fingerprint_guid()
        self.reset_version_guid()

    @property
    def dxfversion(self) -> str:
        """Get current DXF version."""
        return self._dxfversion

    @dxfversion.setter
    def dxfversion(self, version) -> None:
        """Set current DXF version."""
        self._dxfversion = self._validate_dxf_version(version)
        self.header["$ACADVER"] = version

    @property
    def output_encoding(self):
        """Returns required output encoding for writing document to a text
        streams.
        """
        return "utf-8" if self.dxfversion >= DXF2007 else self.encoding

    @property
    def units(self) -> int:
        """Get and set the document/modelspace base units as enum, for more
        information read this: :ref:`dxf units`.

        """
        return self.header.get("$INSUNITS", 0)

    @units.setter
    def units(self, unit_enum: int) -> None:
        if 0 <= unit_enum < 25:
            self.header["$INSUNITS"] = unit_enum
        else:
            raise ValueError(f"Invalid units enum: {unit_enum}")

    def _validate_dxf_version(self, version: str) -> str:
        version = version.upper()
        # translates 'R12' -> 'AC1009'
        version = const.acad_release_to_dxf_version.get(version, version)
        if version not in const.versions_supported_by_save:
            raise const.DXFVersionError(f'Unsupported DXF version "{version}".')
        if version == DXF12:
            if self._dxfversion > DXF12:
                logger.warning(
                    f"Downgrade from DXF {self.acad_release} to R12 may create "
                    f"an invalid DXF file."
                )
        elif version < self._dxfversion:
            logger.info(
                f"Downgrade from DXF {self.acad_release} to "
                f"{const.acad_release[version]} can cause lost of features."
            )
        return version

    @classmethod
    def read(cls, stream: TextIO) -> "Drawing":
        """Open an existing drawing. Package users should use the factory
        function :func:`ezdxf.read`. To preserve possible binary data in
        XRECORD entities use :code:`errors='surrogateescape'` as error handler
        for the import stream.

        Args:
             stream: text stream yielding text (unicode) strings by readline()

        """
        from .lldxf.tagger import ascii_tags_loader

        tag_loader = ascii_tags_loader(stream)
        return cls.load(tag_loader)

    @classmethod
    def load(cls, tag_loader: Iterable["DXFTag"]) -> "Drawing":
        """Load DXF document from a DXF tag loader, in general an external
        untrusted source.

        Args:
            tag_loader: DXF tag loader

        """
        from .lldxf.tagger import tag_compiler

        tag_loader = tag_compiler(tag_loader)
        doc = cls()
        doc._load(tag_loader)
        return doc

    @classmethod
    def from_tags(cls, compiled_tags: Iterable["DXFTag"]) -> "Drawing":
        """Create new drawing from compiled tags. (internal API)"""
        doc = cls()
        doc._load(tagger=compiled_tags)
        return doc

    def _load(self, tagger: Optional[Iterable["DXFTag"]]) -> None:
        # 1st Loading stage: load complete DXF entity structure
        self.is_loading = True
        sections = loader.load_dxf_structure(tagger)
        if "THUMBNAILIMAGE" in sections:
            del sections["THUMBNAILIMAGE"]
        self._load_section_dict(sections)

    def _load_section_dict(self, sections: loader.SectionDict) -> None:
        """Internal API to load a DXF document from a section dict."""
        self.is_loading = True
        # Create header section:
        # All header tags are the first DXF structure entity
        header_entities = sections.get("HEADER", [None])[0]
        if header_entities is None:
            # Create default header, files without header are by default DXF R12
            self.header = HeaderSection.new(dxfversion=DXF12)
        else:
            self.header = HeaderSection.load(header_entities)

        self._dxfversion: str = self.header.get("$ACADVER", DXF12)

        # Store original DXF version of loaded file.
        self._loaded_dxfversion = self._dxfversion

        # Content encoding:
        self.encoding = toencoding(self.header.get("$DWGCODEPAGE", "ANSI_1252"))

        # Set handle seed:
        seed: str = self.header.get("$HANDSEED", str(self.entitydb.handles))
        self.entitydb.handles.reset(_validate_handle_seed(seed))

        # Store all necessary DXF entities in the entity database:
        loader.load_and_bind_dxf_content(sections, self)

        # End of 1. loading stage, all entities of the DXF file are
        # stored in the entity database.

        # Create sections:
        self.classes = ClassesSection(self, sections.get("CLASSES", None))
        self.tables = TablesSection(self, sections.get("TABLES", None))

        # Create *Model_Space and *Paper_Space BLOCK_RECORDS
        # BlockSection setup takes care about the rest:
        self._create_required_block_records()

        # At this point all table entries are required:
        self.blocks = BlocksSection(self, sections.get("BLOCKS", None))
        self.entities = EntitySection(self, sections.get("ENTITIES", None))
        self.objects = ObjectsSection(self, sections.get("OBJECTS", None))

        # only DXF R2013+
        self.acdsdata = AcDsDataSection(self, sections.get("ACDSDATA", None))

        # Store unmanaged sections as raw tags:
        for name, data in sections.items():
            if name not in const.MANAGED_SECTIONS:
                self.stored_sections.append(StoredSection(data))

        # Objects section is not initialized!
        self._2nd_loading_stage()

        # DXF version upgrades:
        if self.dxfversion < DXF12:
            logger.info("DXF version upgrade to DXF R12.")
            self.dxfversion = DXF12

        if self.dxfversion == DXF12:
            self.tables.create_table_handles()

        if self.dxfversion in (DXF13, DXF14):
            logger.info("DXF version upgrade to DXF R2000.")
            self.dxfversion = DXF2000
            self.create_all_arrow_blocks()

        # Objects section setup:
        self.rootdict = self.objects.rootdict
        # Create missing management tables (DICTIONARY):
        self.objects.setup_objects_management_tables(self.rootdict)

        # Setup modelspace- and paperspace layouts:
        self.layouts = Layouts.load(self)

        # Additional work is common to the new and load process:
        self.is_loading = False
        self._finalize_setup()

    def _2nd_loading_stage(self):
        """Load additional resources from entity database into DXF entities.

        e.g. convert handles into DXFEntity() objects

        """
        db = self.entitydb
        for entity in db.values():
            # The post_load_hook() can return a callable, which should be
            # executed, when the DXF document is fully initialized.
            cmd = entity.post_load_hook(self)
            if cmd is not None:
                self._post_init_commands.append(cmd)

    def create_all_arrow_blocks(self):
        """For upgrading DXF R12/13/14 files to R2000, it is necessary to
        create all used arrow blocks before saving the DXF file, else $HANDSEED
        is not the next available handle, which is a problem for AutoCAD.
        To be save create all known AutoCAD arrows, because references to arrow
        blocks can be in DIMSTYLE, DIMENSION override, LEADER override and maybe
        other places.

        """
        from ezdxf.render.arrows import ARROWS

        for arrow_name in ARROWS.__acad__:
            ARROWS.create_block(self.blocks, arrow_name)

    def _create_required_block_records(self):
        if "*Model_Space" not in self.block_records:
            self.block_records.new("*Model_Space")
        if "*Paper_Space" not in self.block_records:
            self.block_records.new("*Paper_Space")

    def saveas(
        self,
        filename: Union[str, "Path"],
        encoding: str = None,
        fmt: str = "asc",
    ) -> None:
        """Set :class:`Drawing` attribute :attr:`filename` to `filename` and
        write drawing to the file system. Override file encoding by argument
        `encoding`, handle with care, but this option allows you to create DXF
        files for applications that handles file encoding different than
        AutoCAD.

        Args:
            filename: file name as string
            encoding: override default encoding as Python encoding string like ``'utf-8'``
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for Binary DXF

        """
        self.filename = str(filename)
        self.save(encoding=encoding, fmt=fmt)

    def save(self, encoding: str = None, fmt: str = "asc") -> None:
        """Write drawing to file-system by using the :attr:`filename` attribute
        as filename. Override file encoding by argument `encoding`, handle with
        care, but this option allows you to create DXF files for applications
        that handles file encoding different than AutoCAD.

        Args:
            encoding: override default encoding as Python encoding string like ``'utf-8'``
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for Binary DXF

        """
        # DXF R12, R2000, R2004 - ASCII encoding
        # DXF R2007 and newer - UTF-8 encoding
        # in ASCII mode, unknown characters will be escaped as \U+nnnn unicode
        # characters.

        if encoding is None:
            enc = self.output_encoding
        else:
            # override default encoding, for applications that handle encoding
            # different than AutoCAD
            enc = encoding

        if fmt.startswith("asc"):
            fp = io.open(
                self.filename, mode="wt", encoding=enc, errors="dxfreplace"
            )
        elif fmt.startswith("bin"):
            fp = open(self.filename, "wb")
        else:
            raise ValueError(f"Unknown output format: '{fmt}'.")
        try:
            self.write(fp, fmt=fmt)
        finally:
            fp.close()

    def encode(self, s: str) -> bytes:
        """Encode string `s` with correct encoding and error handler."""
        return s.encode(encoding=self.output_encoding, errors="dxfreplace")

    def write(self, stream: Union[TextIO, BinaryIO], fmt: str = "asc") -> None:
        """Write drawing as ASCII DXF to a text stream or as Binary DXF to a
        binary stream. For DXF R2004 (AC1018) and prior open stream with
        drawing :attr:`encoding` and :code:`mode='wt'`. For DXF R2007 (AC1021)
        and later use :code:`encoding='utf-8'`, or better use the later added
        :class:`Drawing` property :attr:`output_encoding` which returns the
        correct encoding automatically. The correct and required error handler
        is :code:`errors='dxfreplace'`!

        If writing to a :class:`StringIO` stream, use :meth:`Drawing.encode` to
        encode the result string from :meth:`StringIO.get_value`::

            binary = doc.encode(stream.get_value())

        Args:
            stream: output text stream or binary stream
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for binary DXF

        """
        dxfversion = self.dxfversion
        if dxfversion == DXF12:
            handles = bool(self.header.get("$HANDLING", 0))
        else:
            handles = True
        if dxfversion > DXF12:
            self.classes.add_required_classes(dxfversion)

        self._create_appids()
        self._update_header_vars()
        self.update_extents()
        self.update_limits()
        self._update_metadata()

        if fmt.startswith("asc"):
            tagwriter = TagWriter(
                stream, write_handles=handles, dxfversion=dxfversion
            )
        elif fmt.startswith("bin"):
            tagwriter = BinaryTagWriter(
                stream,
                write_handles=handles,
                dxfversion=dxfversion,
                encoding=self.output_encoding,
            )
            tagwriter.write_signature()
        else:
            raise ValueError(f"Unknown output format: '{fmt}'.")

        self.export_sections(tagwriter)

    def encode_base64(self) -> bytes:
        """Returns DXF document as base64 encoded binary data."""
        stream = io.StringIO()
        self.write(stream)
        # Create binary data:
        binary_data = self.encode(stream.getvalue())
        # Create Windows line endings and do base64 encoding:
        return base64.encodebytes(binary_data.replace(b"\n", b"\r\n"))

    def export_sections(self, tagwriter: "TagWriter") -> None:
        """DXF export sections. (internal API)"""
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

        tagwriter.write_tag2(0, "EOF")

    def update_extents(self):
        msp = self.modelspace()
        self.header["$EXTMIN"] = msp.dxf.extmin
        self.header["$EXTMAX"] = msp.dxf.extmax
        active_layout = self.active_layout()
        self.header["$PEXTMIN"] = active_layout.dxf.extmin
        self.header["$PEXTMAX"] = active_layout.dxf.extmax

    def update_limits(self):
        msp = self.modelspace()
        self.header["$LIMMIN"] = msp.dxf.limmin
        self.header["$LIMMAX"] = msp.dxf.limmax
        active_layout = self.active_layout()
        self.header["$PLIMMIN"] = active_layout.dxf.limmin
        self.header["$PLIMMAX"] = active_layout.dxf.limmax

    def _update_header_vars(self):
        from ezdxf.lldxf.const import acad_maint_ver

        # set or correct $CMATERIAL handle
        material = self.entitydb.get(self.header.get("$CMATERIAL", None))
        if material is None or material.dxftype() != "MATERIAL":
            if "ByLayer" in self.materials:
                self.header["$CMATERIAL"] = self.materials.get(
                    "ByLayer"
                ).dxf.handle
            else:  # set any handle, except '0' which crashes BricsCAD
                self.header["$CMATERIAL"] = "45"

        # set ACAD maintenance version - same values as used by BricsCAD
        self.header["$ACADMAINTVER"] = acad_maint_ver.get(self.dxfversion, 0)

    def _update_metadata(self):
        self._update_ezdxf_metadata()
        if ezdxf.options.write_fixed_meta_data_for_testing:
            fixed_date = juliandate(datetime(2000, 1, 1, 0, 0))
            self.header["$TDCREATE"] = fixed_date
            self.header["$TDUCREATE"] = fixed_date
            self.header["$TDUPDATE"] = fixed_date
            self.header["$TDUUPDATE"] = fixed_date
            self.header["$VERSIONGUID"] = CONST_GUID
            self.header["$FINGERPRINTGUID"] = CONST_GUID
        else:
            now = datetime.now()
            self.header["$TDUPDATE"] = juliandate(now)
            self.reset_version_guid()
        self.header["$HANDSEED"] = str(self.entitydb.handles)  # next handle
        self.header["$DWGCODEPAGE"] = tocodepage(self.encoding)

    def ezdxf_metadata(self) -> "MetaData":
        """Returns the *ezdxf* :class:`ezdxf.document.MetaData` object, which
        manages  *ezdxf* and custom metadata in DXF files.
        For more information see:  :ref:`ezdxf_metadata`.

        .. versionadded:: 0.17

        """
        return (
            R12MetaData(self)
            if self.dxfversion <= DXF12
            else R2000MetaData(self)
        )

    def _create_ezdxf_metadata(self):
        ezdxf_meta = self.ezdxf_metadata()
        ezdxf_meta[CREATED_BY_EZDXF] = ezdxf_marker_string()

    def _update_ezdxf_metadata(self):
        ezdxf_meta = self.ezdxf_metadata()
        ezdxf_meta[WRITTEN_BY_EZDXF] = ezdxf_marker_string()

    def _create_appid_if_not_exist(self, name: str, flags: int = 0) -> None:
        if name not in self.appids:
            self.appids.new(name, {"flags": flags})

    def _create_appids(self):
        self._create_appid_if_not_exist("HATCHBACKGROUNDCOLOR", 0)
        self._create_appid_if_not_exist("EZDXF", 0)

    @property
    def acad_release(self) -> str:
        """Returns the AutoCAD release number like ``'R12'`` or ``'R2000'``."""
        return const.acad_release.get(self.dxfversion, "unknown")

    @property
    def layers(self) -> "Table":
        return self.tables.layers

    @property
    def linetypes(self) -> "Table":
        return self.tables.linetypes

    @property
    def styles(self) -> "Table":
        return self.tables.styles

    @property
    def dimstyles(self) -> "Table":
        return self.tables.dimstyles

    @property
    def ucs(self) -> "Table":
        return self.tables.ucs

    @property
    def appids(self) -> "Table":
        return self.tables.appids

    @property
    def views(self) -> "Table":
        return self.tables.views

    @property
    def block_records(self) -> "Table":
        return self.tables.block_records

    @property
    def viewports(self) -> "ViewportTable":
        return self.tables.viewports

    @property
    def plotstyles(self) -> "Dictionary":
        return self.rootdict["ACAD_PLOTSTYLENAME"]

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

    def modelspace(self) -> "Modelspace":
        """Returns the modelspace layout, displayed as ``'Model'`` tab in CAD
        applications, defined by block record named ``'*Model_Space'``.
        """
        return self.layouts.modelspace()

    def layout(self, name: str = None) -> "Layout":
        """Returns paperspace layout `name` or returns first layout in tab
        order if `name` is ``None``.
        """
        return self.layouts.get(name)

    def active_layout(self) -> "Layout":
        """Returns the active paperspace layout, defined by block record
        name ``'*Paper_Space'``.
        """
        return self.layouts.active_layout()

    def layout_names(self) -> Iterable[str]:
        """Returns all layout names (modelspace ``'Model'`` included) in
        arbitrary order.
        """
        return list(self.layouts.names())

    def layout_names_in_taborder(self) -> Iterable[str]:
        """Returns all layout names (modelspace included, always first name)
        in tab order.
        """
        return list(self.layouts.names_in_taborder())

    def reset_fingerprint_guid(self):
        """Reset fingerprint GUID."""
        self.header["$FINGERPRINTGUID"] = guid()

    def reset_version_guid(self):
        """Reset version GUID."""
        self.header["$VERSIONGUID"] = guid()

    @property
    def acad_compatible(self) -> bool:
        """Returns ``True`` if drawing is AutoCAD compatible."""
        return self._acad_compatible

    def add_acad_incompatibility_message(self, msg: str):
        """Add AutoCAD incompatibility message. (internal API)"""
        self._acad_compatible = False
        if msg not in self._acad_incompatibility_reason:
            self._acad_incompatibility_reason.add(msg)
            logger.warning(
                f"Drawing is incompatible to AutoCAD, because {msg}."
            )

    def query(self, query: str = "*") -> EntityQuery:
        """
        Entity query over all layouts and blocks, excluding the OBJECTS section.

        Args:
            query: query string

        .. seealso::

            :ref:`entity query string` and :ref:`entity queries`

        """
        return EntityQuery(self.chain_layouts_and_blocks(), query)

    def groupby(self, dxfattrib="", key=None) -> dict:
        """Groups DXF entities of all layouts and blocks (excluding the
        OBJECTS section) by a DXF attribute or a key function.

        Args:
            dxfattrib: grouping DXF attribute like ``'layer'``
            key: key function, which accepts a :class:`DXFEntity` as argument
                and returns a hashable grouping key or ``None`` to ignore
                this entity.

        .. seealso::

            :func:`~ezdxf.groupby.groupby` documentation

        """
        return groupby(self.chain_layouts_and_blocks(), dxfattrib, key)

    def chain_layouts_and_blocks(self) -> Iterable["DXFEntity"]:
        """Chain entity spaces of all layouts and blocks. Yields an iterator
        for all entities in all layouts and blocks.

        """
        layouts = list(self.layouts_and_blocks())
        return chain.from_iterable(layouts)

    def layouts_and_blocks(self) -> Iterable["GenericLayoutType"]:
        """Iterate over all layouts (modelspace and paperspace) and all
        block definitions.

        """
        return iter(self.blocks)

    def delete_layout(self, name: str) -> None:
        """
        Delete paper space layout `name` and all entities owned by this layout.
        Available only for DXF R2000 or later, DXF R12 supports only one
        paperspace and it can't be deleted.

        """
        if name not in self.layouts:
            raise const.DXFValueError(f"Layout '{name}' does not exist.")
        else:
            self.layouts.delete(name)

    def new_layout(self, name, dxfattribs=None) -> "Layout":
        """
        Create a new paperspace layout `name`. Returns a
        :class:`~ezdxf.layouts.Layout` object.
        DXF R12 (AC1009) supports only one paperspace layout, only the active
        paperspace layout is saved, other layouts are dismissed.

        Args:
            name: unique layout name
            dxfattribs: additional DXF attributes for the
                :class:`~ezdxf.entities.layout.DXFLayout` entity

        Raises:
            DXFValueError: :class:`~ezdxf.layouts.Layout` `name` already exist

        """
        if name in self.layouts:
            raise const.DXFValueError(f"Layout '{name}' already exists.")
        else:
            return self.layouts.new(name, dxfattribs)

    def acquire_arrow(self, name: str):
        """For standard AutoCAD and ezdxf arrows create block definitions if
        required, otherwise check if block `name` exist. (internal API)

        """
        from ezdxf.render.arrows import ARROWS

        if ARROWS.is_acad_arrow(name) or ARROWS.is_ezdxf_arrow(name):
            ARROWS.create_block(self.blocks, name)
        elif name not in self.blocks:
            raise const.DXFValueError(f'Arrow block "{name}" does not exist.')

    def add_image_def(
        self, filename: str, size_in_pixel: Tuple[int, int], name=None
    ):
        """Add an image definition to the objects section.

        Add an :class:`~ezdxf.entities.image.ImageDef` entity to the drawing
        (objects section). `filename` is the image file name as relative or
        absolute path and `size_in_pixel` is the image size in pixel as (x, y)
        tuple. To avoid dependencies to external packages, `ezdxf` can not
        determine the image size by itself. Returns a
        :class:`~ezdxf.entities.image.ImageDef` entity which is needed to
        create an image reference. `name` is the internal image name, if set to
        ``None``, name is auto-generated.

        Absolute image paths works best for AutoCAD but not really good, you
        have to update external references manually in AutoCAD, which is not
        possible in TrueView. If the drawing units differ from 1 meter, you
        also have to use: :meth:`set_raster_variables`.

        Args:
            filename: image file name (absolute path works best for AutoCAD)
            size_in_pixel: image size in pixel as (x, y) tuple
            name: image name for internal use, None for using filename as name
                (best for AutoCAD)

        .. seealso::

            :ref:`tut_image`

        """
        if "ACAD_IMAGE_VARS" not in self.rootdict:
            self.objects.set_raster_variables(frame=0, quality=1, units="m")
        if name is None:
            name = filename
        return self.objects.add_image_def(filename, size_in_pixel, name)

    def set_raster_variables(
        self, frame: int = 0, quality: int = 1, units: str = "m"
    ):
        """
        Set raster variables.

        Args:
            frame: ``0`` = do not show image frame; ``1`` = show image frame
            quality: ``0`` = draft; ``1`` = high
            units: units for inserting images. This defines the real world unit
                for one drawing unit for the purpose of inserting and scaling
                images with an associated resolution.

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
        self.objects.set_raster_variables(
            frame=frame, quality=quality, units=units
        )

    def set_wipeout_variables(self, frame=0):
        """
        Set wipeout variables.

        Args:
            frame: ``0`` = do not show image frame; ``1`` = show image frame

        """
        self.objects.set_wipeout_variables(frame=frame)
        var_dict = self.rootdict.get_required_dict("AcDbVariableDictionary")
        var_dict.set_or_add_dict_var("WIPEOUTFRAME", str(frame))

    def add_underlay_def(
        self, filename: str, format: str = "ext", name: str = None
    ):
        """Add an :class:`~ezdxf.entities.underlay.UnderlayDef` entity to the
        drawing (OBJECTS section).
        `filename` is the underlay file name as relative or absolute path and
        `format` as string (pdf, dwf, dgn).
        The underlay definition is required to create an underlay reference.

        Args:
            filename: underlay file name
            format: file format as string ``'pdf'|'dwf'|'dgn'`` or ``'ext'``
                for getting file format from filename extension
            name: pdf format = page number to display; dgn format =
                ``'default'``; dwf: ????

        .. seealso::

            :ref:`tut_underlay`

        """
        if format == "ext":
            format = filename[-3:]
        return self.objects.add_underlay_def(filename, format, name)

    def add_xref_def(
        self, filename: str, name: str, flags: int = BLK_XREF | BLK_EXTERNAL
    ):
        """
        Add an external reference (xref) definition to the blocks section.

        Args:
            filename: external reference filename
            name: name of the xref block
            flags: block flags

        """
        self.blocks.new(
            name=name, dxfattribs={"flags": flags, "xref_path": filename}
        )

    def audit(self) -> "Auditor":
        """Checks document integrity and fixes all fixable problems, not
        fixable problems are stored in :attr:`Auditor.errors`.

        If you are messing around with internal structures, call this method
        before saving to be sure to export valid DXF documents, but be aware
        this is a long running task.

        """
        from ezdxf.audit import Auditor

        auditor = Auditor(self)
        auditor.run()
        return auditor

    def validate(self, print_report=True) -> bool:
        """Simple way to run an audit process. Fixes all fixable problems,
        return ``False`` if not fixable errors occurs, to get more information
        about not fixable errors use :meth:`audit` method instead.

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

    def set_modelspace_vport(self, height, center=(0, 0)) -> "VPort":
        r"""Set initial view/zoom location for the modelspace, this replaces
        the current "\*Active" viewport configuration.

        Args:
             height: modelspace area to view
             center: modelspace location to view in the center of the CAD
                application window.

        """
        self.viewports.delete_config("*Active")
        vport = cast("VPort", self.viewports.new("*Active"))
        vport.dxf.center = center
        vport.dxf.height = height
        return vport


class MetaData(abc.ABC):
    """Manage ezdxf meta data by dict-like interface. Values are limited to
    strings with a maximum length of 254 characters.
    """

    @abc.abstractmethod
    def __getitem__(self, key: str) -> str:
        """Returns the value for `key`. Raises a :class:`KeyError` exception
        if `key` not exist.
        """
        ...

    def get(self, key: str, default: str = "") -> str:
        """Returns the value for `key`. Returns `default` if `key` not exist."""
        try:
            return self.__getitem__(key)
        except KeyError:
            return safe_string(default)

    @abc.abstractmethod
    def __setitem__(self, key: str, value: str) -> None:
        """Set `key` to `value`. """
        ...

    @abc.abstractmethod
    def __delitem__(self, key: str) -> None:
        """Remove `key`, raises a :class:`KeyError` exception if `key` not
        exist.
        """
        ...

    @abc.abstractmethod
    def __contains__(self, key: str) -> bool:
        """Returns ``True`` if `key` exist. """
        ...

    def discard(self, key: str) -> None:
        """Remove `key`, does **not** raise an exception if `key` not exist. """
        try:
            self.__delitem__(key)
        except KeyError:
            pass


def ezdxf_marker_string():
    if ezdxf.options.write_fixed_meta_data_for_testing:
        return CONST_MARKER_STRING
    else:
        now = datetime.now(tz=timezone.utc)
        return ezdxf.__version__ + " @ " + now.isoformat()


def safe_string(s: str) -> str:
    return escape_dxf_line_endings(s)[:254]


class R12MetaData(MetaData):
    """Manage ezdxf meta data for DXF version R12 as XDATA of layer "0".

    Layer "0" is mandatory and can not be deleted.

    """

    def __init__(self, doc: Drawing):
        # storing XDATA in layer 0 does not work (Autodesk!)
        self._msp_block = doc.modelspace().block_record.block
        self._data = self._load()

    def __contains__(self, key: str) -> bool:
        return safe_string(key) in self._data

    def __getitem__(self, key: str) -> str:
        return self._data[safe_string(key)]

    def __setitem__(self, key: str, value: str) -> None:
        self._data[safe_string(key)] = safe_string(value)
        self._commit()

    def __delitem__(self, key: str) -> None:
        del self._data[safe_string(key)]
        self._commit()

    def _commit(self) -> None:
        # write all metadata as strings with group code 1000
        tags = []
        for key, value in self._data.items():
            tags.append((1000, str(key)))
            tags.append((1000, str(value)))
        self._msp_block.set_xdata("EZDXF", tags)

    def _load(self) -> Dict:
        data = dict()
        if self._msp_block.has_xdata("EZDXF"):
            xdata = self._msp_block.get_xdata("EZDXF")
            index = 0
            count = len(xdata) - 1
            while index < count:
                name = xdata[index].value
                data[name] = xdata[index + 1].value
                index += 2
        return data


class R2000MetaData(MetaData):
    """Manage ezdxf meta data for DXF version R2000+ as DICTIONARY object in
    the rootdict.
    """

    def __init__(self, doc: Drawing):
        self._data: "Dictionary" = doc.rootdict.get_required_dict(
            EZDXF_META
        )

    def __contains__(self, key: str) -> bool:
        return safe_string(key) in self._data

    def __getitem__(self, key: str) -> str:
        v = self._data[safe_string(key)]
        return v.dxf.get("value", "")

    def __setitem__(self, key: str, value: str) -> None:
        self._data.set_or_add_dict_var(safe_string(key), safe_string(value))

    def __delitem__(self, key: str) -> None:
        self._data.remove(safe_string(key))
