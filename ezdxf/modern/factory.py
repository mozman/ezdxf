# Created: 12.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from ezdxf.legacy import LegacyDXFFactory
from ezdxf.tools.handle import ImageKeyGenerator, UnderlayKeyGenerator
from ezdxf.lldxf.const import DXFKeyError

from . import tableentries
from . import graphics
from . import solid3d
from . import surface
from . import polyline
from . import trace
from . import block
from . import attrib
from . import ray
from .text import Text
from .insert import Insert
from .lwpolyline import LWPolyline
from .ellipse import Ellipse
from .mesh import Mesh
from .spline import Spline
from .mtext import MText
from .hatch import Hatch
from .viewport import Viewport
from .image import Image
from .image import ImageDef, ImageDefReactor, RasterVariables
from .underlay import PdfDefinition, PdfUnderlay
from .underlay import DwfDefinition, DwfUnderlay
from .underlay import DgnDefinition, DgnUnderlay
from .dxflayout import DXFPlotSettings, DXFLayout
from .dimension import Dimension
from .acad_proxy_entity import ProxyEntity, ProxyObject
from .helix import Helix
from .leader import Leader
from .light import Light
from .mleader import MLeader, MLeaderStyle
from .mline import MLine, MLineStyle
from .oleframe import OLE2Frame, OLEFrame
from .section import Section
from .sun import Sun
from .sunstudy import SunStudy
from .tolerance import Tolerance
from .wipeout import Wipeout, WipeoutVariables
from .acad_table import ACADTable
from .tablestyle import TableStyle
from .idbuffer import IDBuffer
from .fieldlist import FieldList
from .field import Field
from .layer_filter import LayerFilter
from .sortentstable import SortEntitiesTable
from .dimassoc import DimAssoc
from .vba_project import VBAProject
from .visualstyle import VisualStyle

from . import dxfobjects
from . import dxfdict
from .xrecord import XRecord
from .datatable import DataTable
from .geodata import GeoData
from .material import Material
from .groups import DXFGroup
from .layouts import Layouts, BlockLayout


UPDATE_ENTITY_WRAPPERS = {
    # DXF Objects
    'DICTIONARY': dxfdict.DXFDictionary,
    'CLASS': dxfobjects.DXFClass,
    'ACDBDICTIONARYWDFLT': dxfdict.DXFDictionaryWithDefault,
    'DICTIONARYVAR': dxfdict.DXFDictionaryVar,
    'PLOTSETTINGS': DXFPlotSettings,
    'LAYOUT': DXFLayout,
    'XRECORD': XRecord,
    'DATATABLE': DataTable,
    'GROUP': DXFGroup,
    'ACDBPLACEHOLDER': dxfobjects.ACDBPlaceHolder,
    'IMAGEDEF': ImageDef,
    'IMAGEDEF_REACTOR': ImageDefReactor,
    'PDFDEFINITION': PdfDefinition,
    'DWFDEFINITION': DwfDefinition,
    'DGNDEFINITION': DgnDefinition,
    'RASTERVARIABLES': RasterVariables,
    'GEODATA': GeoData,
    'MATERIAL': Material,
    'ACAD_PROXY_OBJECT': ProxyObject,
    'MLEADERSTYLE': MLeaderStyle,
    'MLINESTYLE': MLineStyle,
    'SUN': Sun,
    'SUNSTUDY': SunStudy,
    'WIPEOUTVARIABLES': WipeoutVariables,
    'TABLESTYLE': TableStyle,
    'IDBUFFER': IDBuffer,
    'FIELDLIST': FieldList,
    'FIELD': Field,
    'LAYER_FILTER': LayerFilter,
    'SORTENTSTABLE': SortEntitiesTable,
    'DIMASSOC': DimAssoc,
    'VBA_PROJECT': VBAProject,
    # DXF Table Entries
    'LAYER': tableentries.Layer,
    'STYLE': tableentries.Style,
    'LTYPE': tableentries.Linetype,
    'DIMSTYLE': tableentries.DimStyle,
    'VIEW': tableentries.View,
    'VPORT': tableentries.VPort,
    'UCS': tableentries.UCS,
    'APPID': tableentries.AppID,
    'BLOCK_RECORD': tableentries.BlockRecord,
    # DXF Entities
    'LINE': graphics.Line,
    'POINT': graphics.Point,
    'CIRCLE': graphics.Circle,
    'ARC': graphics.Arc,
    'TRACE': trace.Trace,
    'SOLID': trace.Solid,
    '3DFACE': trace.Face,
    'TEXT': Text,
    'MTEXT': MText,
    'POLYLINE': polyline.Polyline,
    'VERTEX': polyline.Vertex,
    'SEQEND': graphics.SeqEnd,
    'LWPOLYLINE': LWPolyline,
    'BLOCK': block.Block,
    'ENDBLK': block.EndBlk,
    'INSERT': Insert,
    'ATTDEF': attrib.Attdef,
    'ATTRIB': attrib.Attrib,
    'ELLIPSE': Ellipse,
    'RAY': ray.Ray,
    'XLINE': ray.XLine,
    'SHAPE': graphics.Shape,
    'SPLINE': Spline,
    'BODY': solid3d.Body,
    'REGION': solid3d.Region,
    '3DSOLID': solid3d.Solid3d,
    'SURFACE': surface.Surface,
    'EXTRUDEDSURFACE': surface.ExtrudedSurface,
    'LOFTEDSURFACE': surface.LoftedSurface,
    'REVOLVEDSURFACE': surface.RevolvedSurface,
    'SWEPTSURFACE': surface.SweptSurface,
    'MESH': Mesh,
    'HATCH': Hatch,
    'VIEWPORT': Viewport,
    'IMAGE': Image,
    'PDFUNDERLAY': PdfUnderlay,
    'DWFUNDERLAY': DwfUnderlay,
    'DGNUNDERLAY': DgnUnderlay,
    'DIMENSION': Dimension,
    'ACAD_PROXY_ENTITY': ProxyEntity,
    'HELIX': Helix,
    'LEADER': Leader,
    'LIGHT': Light,
    'MLEADER': MLeader,
    'MLINE': MLine,
    'OLEFRAME': OLEFrame,
    'OLE2FRAME': OLE2Frame,
    'SECTION': Section,
    'TOLERANCE': Tolerance,
    'WIPEOUT': Wipeout,
    'ACAD_TABLE': ACADTable,
    'VISUALSTYLE': VisualStyle,
}


class ModernDXFFactory(LegacyDXFFactory):
    """ DXf factory for DXF version AC1015 and later. (changed 04.05.2014)
    """
    DEFAULT_WRAPPER = graphics.ModernGraphicEntity

    def __init__(self, drawing):
        super(ModernDXFFactory, self).__init__(drawing)
        self.ENTITY_WRAPPERS.update(UPDATE_ENTITY_WRAPPERS)
        self.image_key_generator = ImageKeyGenerator()
        self.underlay_key_generator = UnderlayKeyGenerator()

    @property
    def rootdict(self):
        return self.drawing.rootdict

    @property
    def block_records(self):
        return self.drawing.sections.tables.block_records

    def create_block_entry_in_block_records_table(self, block_layout):
        # required for DXFVERSION > ac1009: Entry in the BLOCK_RECORDS section
        block_record = self.block_records.new(block_layout.name)
        block_layout.set_block_record_handle(block_record.dxf.handle)

    def get_layouts(self):
        return Layouts(self.drawing)

    def new_block_layout(self, block_handle, endblk_handle):
        # Warning: Do not call create_block_entry_in_block_records_table() from this point, this will not work!
        return BlockLayout(self.entitydb, self, block_handle, endblk_handle)

    def copy_layout(self, source_entity, target_entity):
        # Place target_entity in same layout as source_entity
        target_entity.dxf.paperspace = source_entity.dxf.paperspace
        target_entity.dxf.owner = source_entity.dxf.owner

    def next_image_key(self, checkfunc=lambda k: True):
        while True:
            key = self.image_key_generator.next()
            if checkfunc(key):
                return key

    def next_underlay_key(self, checkfunc=lambda k: True):
        while True:
            key = self.underlay_key_generator.next()
            if checkfunc(key):
                return key

    def get_layout_for_entity(self, entity):
        if entity.dxf.owner not in self.entitydb:
            return None

        dwg = self.drawing
        try:
            layout = dwg.layouts.get_layout_for_entity(entity)
        except DXFKeyError:
            block_rec = dwg.dxffactory.wrap_handle(entity.dxf.owner)
            block_name = block_rec.dxf.name
            layout = dwg.blocks.get(block_name)
        return layout
