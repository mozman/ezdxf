# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13

# first factory
from . import factory

# basic classes
from .xdict import ExtensionDict
from .xdata import XData, EmbeddedObjects
from .appdata import AppData, Reactors
from .dxfentity import DXFEntity
from .dxfgfx import DXFGraphic
from .dxfobj import DXFObject

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
from .dxfobj import XRecord, AcDbPlaceholder, VBAProject, SortEntsTable
from .dictionary import Dictionary, DictionaryVar, DictionaryWithDefault
from .layout import DXFLayout
from .idbuffer import IDBuffer
from .sun import Sun

# register DXF objects R2007
from .visualstyle import VisualStyle

# register entities R12
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


