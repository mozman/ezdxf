# Created: 11.12.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
"""
ezdxf typing collection

Only usable in type checking mode:

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFTag

"""
from typing import *

if TYPE_CHECKING:
    # Low level stuff
    from ezdxf.algebra.vector import Vector
    from ezdxf.tools.handle import HandleGenerator
    from ezdxf.lldxf.types import DXFTag, DXFBinaryTag, DXFVertex
    from ezdxf.lldxf.attributes import XType, DXFAttr
    from ezdxf.lldxf.tags import Tags
    from ezdxf.lldxf.extendedtags import ExtendedTags
    from ezdxf.lldxf.tagwriter import TagWriter

    # Entity factories
    from ezdxf.legacy.factory import LegacyDXFFactory
    from ezdxf.modern.factory import ModernDXFFactory

    from ezdxf.legacy.layouts import DXF12Layout, DXF12BlockLayout
    from ezdxf.modern.layouts import Layout, BlockLayout

    # Entities manager
    from ezdxf.entityspace import EntitySpace
    from ezdxf.drawing import Drawing
    from ezdxf.database import EntityDB

    # Sections and Tables
    from ezdxf.sections.table import Table, ViewportTable
    from ezdxf.sections.blocks import BlocksSection
    from ezdxf.sections.header import HeaderSection
    from ezdxf.sections.tables import TablesSection
    from ezdxf.sections.blocks import BlocksSection
    from ezdxf.sections.classes import ClassesSection
    from ezdxf.sections.objects import ObjectsSection
    from ezdxf.sections.entities import EntitySection
    from ezdxf.sections.unsupported import UnsupportedSection

    # Table entries
    from ezdxf.modern.tableentries import BlockRecord, Layer, Linetype, Style, DimStyle
    from ezdxf.modern.tableentries import UCS, View, AppID, VPort

    # Style Manager
    from ezdxf.modern.groups import GroupManager
    from ezdxf.modern.material import MaterialManager
    from ezdxf.modern.mleader import MLeaderStyleManager
    from ezdxf.modern.mline import MLineStyleManager

    # DXF objects
    from ezdxf.modern.dxfdict import DXFDictionary
    from ezdxf.modern.geodata import GeoData
    from ezdxf.modern.sortentstable import SortEntitiesTable

    # DXF entities
    from ezdxf.dxfentity import DXFEntity
    from ezdxf.modern.spline import Spline
    from ezdxf.legacy.polyline import Polyline, Polyface, Polymesh, DXFVertex
    from ezdxf.legacy.attrib import Attdef, Attrib
    from ezdxf.legacy.text import Text
    from ezdxf.modern.viewport import Viewport
    from ezdxf.modern.block import Block

    # other
    from ezdxf.audit import Auditor

    # Type compositions
    Vertex = Union[Sequence[float], Vector]
    TagValue = Union[str, int, float, Sequence[float]]
    RGB = Tuple[int, int, int]
    IterableTags = Iterable[Tuple[int, TagValue]]
    SectionDict = Dict[str, List[Union[Tags, ExtendedTags]]]
    KeyFunc = Callable[['DXFEntity'], Hashable]
    FaceType = Sequence[Vertex]

    # Type Unions
    DXFFactoryType = Union[LegacyDXFFactory, ModernDXFFactory]
    LayoutType = Union[DXF12Layout, Layout]
    BlockLayoutType = Union[DXF12BlockLayout, BlockLayout]
    GenericLayoutType = Union[LayoutType, BlockLayoutType]
    SectionType = Union[
        HeaderSection, TablesSection, BlocksSection, ClassesSection, ObjectsSection, EntitySection, UnsupportedSection]
