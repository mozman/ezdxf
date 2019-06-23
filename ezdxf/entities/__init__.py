# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# Unified Entity System (UES) with unified DXF attribute system for DXF R12 and DXF R2000+
# ========================================================================================
#
# 1. Store entities as DXFEntity () or inherited instances in the drawing database
# 2. remove separation of legacy and modern tag structures
#    - uses owner tag of DXF R2000+ also for DXF R12
#    - same layout structures (BLOCK_RECORDS, LAYOUT, OBJECTS section)
#    - just don't export DXF R2000+ structures to DXF R12 files
# 3. still store unknown entities (Map3d...) as bunch of tag, but inside of an special DXFEntity (DXFTagStorage)
# 4. preserve actual DXFEntity interface, DXFEntity.dxf seem still a good idea - other methods deprecate slowly
# 5. use individual DXF export functions for each entity, but provide a useful boiler plate

# first factory
from . import factory

# register management structures
from .dxfclass import DXFClass
from .table import TableHead

# register table entries
from .ltype import Linetype
from .layer import Layer
from .textstyle import Textstyle
from .dimstyle import DimStyle
from .view import View
from .vport import VPort
from .ucs import UCSTable
from .appid import AppID
from .blockrecord import BlockRecord

# register DXF objects R2000
from .dxfobj import DXFObject
from .dictionary import Dictionary, DictionaryVar, DictionaryWithDefault
from .layout import DXFLayout
from .idbuffer import IDBuffer
from .sun import Sun

# register DXF objects R2007
from .visualstyle import VisualStyle

# register entities R12
from .dxfentity import DXFEntity
from .dxfgfx import DXFGraphic

from .line import Line
from .point import Point
from .circle import Circle
from .arc import Arc
from .shape import Shape
from .solid import Solid, Face3d, Trace
from .text import Text
from .insert import Insert
from .block import Block, EndBlk
from .polyline import Polyline, Polyface, Polymesh
from .attrib import Attrib, AttDef
from .dimension import Dimension
from .viewport import Viewport


# register graphical entities R2000
from .lwpolyline import LWPolyline
from .ellipse import Ellipse
from .xline import XLine
from .mtext import MText
from .spline import Spline
from .mesh import Mesh
from .hatch import Hatch
from .image import Image, ImageDef
from .underlay import Underlay, UnderlayDef
from .leader import Leader
from .tolerance import Tolerance
from .helix import Helix
from .acis import Body, Solid3d, Region, Surface, ExtrudedSurface, LoftedSurface, RevolvedSurface, SweptSurface

# register graphical entities R2004

# register graphical entities R2007

from .light import Light

# register graphical entities R2010

from .geodata import GeoData

# register graphical entities R2013

# register graphical entities R2018


