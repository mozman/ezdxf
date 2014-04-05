# Purpose: ac1015 table entries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..tags import DXFTag
from ..classifiedtags import ClassifiedTags
from ..ac1009 import tableentries as ac1009
from ..entity import GenericWrapper
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass

_LAYERTEMPLATE = """  0
LAYER
  5
LayerHandle
100
AcDbSymbolTableRecord
100
AcDbLayerTableRecord
  2
LayerName
 70
0
 62
7
  6
Continuous
290
  1
390
0
"""

# code 390 is required for AutoCAD
# Pointer/handle to PlotStyleName
# uses tag(390, ...) from the '0' layer

none_subclass = DefSubclass(None, {
    'handle': DXFAttr(5, None),
    'owner': DXFAttr(330, None),
})

symbol_subclass = DefSubclass('AcDbSymbolTableRecord', {})

layer_subclass = DefSubclass('AcDbLayerTableRecord', {
    'name': DXFAttr(2, None),  # layer name
    'flags': DXFAttr(70, None),
    'color': DXFAttr(62, None),  # dxf color index
    'linetype': DXFAttr(6, None),  # linetype name
    'plot': DXFAttr(290, None),  # don't plot this layer if 0 else 1
    'line_weight': DXFAttr(370, None),  # enum value???
    'plot_style_name': DXFAttr(390, None),  # handle to PlotStyleName object
})


class Layer(ac1009.Layer):
    TEMPLATE = ClassifiedTags.from_text(_LAYERTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, layer_subclass)

    @classmethod
    def new(cls, handle, dxfattribs=None, dxffactory=None):
        layer = super(Layer, cls).new(handle, dxfattribs, dxffactory)
        layer.dxf.plot_style_name = dxffactory.rootdict['ACAD_PLOTSTYLENAME']
        return layer

_STYLETEMPLATE = """  0
STYLE
  5
0
100
AcDbSymbolTableRecord
100
AcDbTextStyleTableRecord
  2
STYLENAME
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
0.2
  3
arial.ttf
  4

"""
style_subclass = DefSubclass('AcDbTextStyleTableRecord', {
    'name': DXFAttr(2, None),
    'flags': DXFAttr(70, None),
    'height': DXFAttr(40, None),  # fixed height, 0 if not fixed
    'width': DXFAttr(41, None),  # width factor
    'oblique': DXFAttr(50, None),  # oblique angle in degree, 0 = vertical
    'generation_flags': DXFAttr(71, None),  # 2 = backward, 4 = mirrored in Y
    'last_height': DXFAttr(42, None),  # last height used
    'font': DXFAttr(3, None),  # primary font file name
    'bigfont': DXFAttr(4, None),  # big font name, blank if none
})


class Style(ac1009.Style):
    TEMPLATE = ClassifiedTags.from_text(_STYLETEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, style_subclass)

_LTYPETEMPLATE = """  0
LTYPE
  5
0
100
AcDbSymbolTableRecord
100
AcDbLinetypeTableRecord
  2
LTYPENAME
 70
0
  3
LTYPEDESCRIPTION
 72
65
"""
linetype_subclass = DefSubclass('AcDbLinetypeTableRecord', {
    'name': DXFAttr(2,  None),
    'description': DXFAttr(3, None),
    'length': DXFAttr(40, None),
    'items': DXFAttr(73, None),
})


class Linetype(ac1009.Linetype):
    TEMPLATE = ClassifiedTags.from_text(_LTYPETEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, linetype_subclass)

    def _setup_pattern(self, pattern):
        subclass = self.tags.get_subclass('AcDbLinetypeTableRecord')
        subclass.append(DXFTag(73, len(pattern) - 1))
        subclass.append(DXFTag(40, float(pattern[0])))

        for element in pattern[1:]:
            subclass.append(DXFTag(49, float(element)))
            subclass.append(DXFTag(74, 0))

_APPIDTEMPLATE = """  0
APPID
  5
0
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
APPIDNAME
 70
0
"""
appid_subclass = DefSubclass('AcDbRegAppTableRecord', {
    'name': DXFAttr(2, None),
    'flags': DXFAttr(70, None),
})


class AppID(ac1009.AppID):
    TEMPLATE = ClassifiedTags.from_text(_APPIDTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, appid_subclass)

_DIMSTYLETEMPLATE = """  0
DIMSTYLE
105
0
100
AcDbSymbolTableRecord
100
AcDbDimStyleTableRecord
  2
STANDARD
 70
0
  3

  4

  5

  6

  7

 40
1.0
 41
3.0
 42
2.0
 43
9.0
 44
5.0
 45
0.0
 46
0.0
 47
0.0
 48
0.0
140
3.0
141
2.0
142
0.0
143
25.399999999999999
144
1.0
145
0.0
146
1.0
147
2.0
 71
     0
 72
     0
 73
     1
 74
     1
 75
     0
 76
     0
 77
     0
 78
     0
170
     0
171
     2
172
     0
173
     0
174
     0
175
     0
176
     0
177
     0
178
     0
"""
handle105_subclass = DefSubclass(None, {
    'handle': DXFAttr(105, None),
    'owner': DXFAttr(330, None),
})

dimstyle_subclass = DefSubclass('AcDbDimStyleTableRecord', {
    'name': DXFAttr(2,  None),
    'flags': DXFAttr(70, None),
    'dimpost': DXFAttr(3, None),
    'dimapost': DXFAttr(4, None),
    'dimblk': DXFAttr(5, None),
    'dimblk1': DXFAttr(6, None),
    'dimblk2': DXFAttr(7, None),
    'dimscale': DXFAttr(40, None),
    'dimasz': DXFAttr(41, None),
    'dimexo': DXFAttr(42, None),
    'dimdli': DXFAttr(43, None),
    'dimexe': DXFAttr(44, None),
    'dimrnd': DXFAttr(45, None),
    'dimdle': DXFAttr(46, None),
    'dimtp': DXFAttr(47, None),
    'dimtm': DXFAttr(48, None),
    'dimtxt': DXFAttr(140, None),
    'dimcen': DXFAttr(141, None),
    'dimtsz': DXFAttr(142, None),
    'dimaltf': DXFAttr(143, None),
    'dimlfac': DXFAttr(144, None),
    'dimtvp': DXFAttr(145, None),
    'dimtfac': DXFAttr(146, None),
    'dimgap': DXFAttr(147, None),
    'dimtol': DXFAttr(71, None),
    'dimlim': DXFAttr(72, None),
    'dimtih': DXFAttr(73, None),
    'dimtoh': DXFAttr(74, None),
    'dimse1': DXFAttr(75, None),
    'dimse2': DXFAttr(76, None),
    'dimtad': DXFAttr(77, None),
    'dimzin': DXFAttr(78, None),
    'dimalt': DXFAttr(170, None),
    'dimaltd': DXFAttr(171, None),
    'dimtofl': DXFAttr(172, None),
    'dimsah': DXFAttr(173, None),
    'dimtix': DXFAttr(174, None),
    'dimsoxd': DXFAttr(175, None),
    'dimclrd': DXFAttr(176, None),
    'dimclre': DXFAttr(177, None),
    'dimclrt': DXFAttr(178, None),
})


class DimStyle(ac1009.DimStyle):
    TEMPLATE = ClassifiedTags.from_text(_DIMSTYLETEMPLATE)
    DXFATTRIBS = DXFAttributes(handle105_subclass, symbol_subclass, dimstyle_subclass)

_UCSTEMPLATE = """  0
UCS
  5
0
100
AcDbSymbolTableRecord
100
AcDbUCSTableRecord
  2
UCSNAME
 70
0
 10
0.0
 20
0.0
 30
0.0
 11
1.0
 21
0.0
 31
0.0
 12
0.0
 22
1.0
 32
0.0
"""
ucs_subclass = DefSubclass('AcDbUCSTableRecord', {
    'name': DXFAttr(2, None),
    'flags': DXFAttr(70, None),
    'origin': DXFAttr(10, 'Point3D'),
    'xaxis': DXFAttr(11, 'Point3D'),
    'yaxis': DXFAttr(12, 'Point3D'),
})


class UCS(ac1009.UCS):
    TEMPLATE = ClassifiedTags.from_text(_UCSTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, ucs_subclass)

_VIEWTEMPLATE = """  0
VIEW
  5
0
100
AcDbSymbolTableRecord
100
AcDbViewTableRecord
  2
VIEWNAME
 70
0
 10
0.0
 20
0.0
 11
1.0
 21
1.0
 31
1.0
 12
0.0
 22
0.0
 32
0.0
 40
70.
 41
1.0
 42
50.0
 43
0.0
 44
0.0
 50
0.0
 71
0
"""
view_subclass = DefSubclass('AcDbViewTableRecord', {
    'name': DXFAttr(2, None),
    'flags': DXFAttr(70, None),
    'height': DXFAttr(40, None),
    'width': DXFAttr(41, None),
    'center_point': DXFAttr(10, 'Point2D'),
    'direction_point': DXFAttr(11, 'Point3D'),
    'target_point': DXFAttr(12, 'Point3D'),
    'lens_length': DXFAttr(42, None),
    'front_clipping': DXFAttr(43, None),
    'back_clipping': DXFAttr(44, None),
    'view_twist': DXFAttr(50, None),
    'view_mode': DXFAttr(71, None),
})


class View(ac1009.View):
    TEMPLATE = ClassifiedTags.from_text(_VIEWTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, view_subclass)

_VPORTTEMPLATE = """  0
VPORT
  5
0
100
AcDbSymbolTableRecord
100
AcDbViewportTableRecord
  2
VPORTNAME
 70
0
 10
0.0
 20
0.0
 11
1.0
 21
1.0
 12
70.0
 22
50.0
 13
0.0
 23
0.0
 14
0.5
 24
0.5
 15
0.5
 25
0.5
 16
0.0
 26
0.0
 36
1.0
 17
0.0
 27
0.0
 37
0.0
 40
70.
 41
1.34
 42
50.0
 43
0.0
 44
0.0
 50
0.0
 51
0.0
 71
0
 72
1000
 73
1
 74
3
 75
0
 76
0
 77
0
 78
0
"""
vport_subclass = DefSubclass('AcDbViewportTableRecord', {
    'name': DXFAttr(2,  None),
    'flags': DXFAttr(70,  None),
    'lower_left': DXFAttr(10, 'Point2D'),
    'upper_right': DXFAttr(11, 'Point2D'),
    'center_point': DXFAttr(12, 'Point2D'),
    'snap_base': DXFAttr(13, 'Point2D'),
    'snap_spacing': DXFAttr(14, 'Point2D'),
    'grid_spacing': DXFAttr(15, 'Point2D'),
    'direction_point': DXFAttr(16, 'Point3D'),
    'target_point': DXFAttr(17, 'Point3D'),
    'height': DXFAttr(40, None),
    'aspect_ratio': DXFAttr(41, None),
    'lens_length': DXFAttr(42, None),
    'front_clipping': DXFAttr(43, None),
    'back_clipping': DXFAttr(44, None),
    'snap_rotation': DXFAttr(50, None),
    'view_twist': DXFAttr(51, None),
    'status': DXFAttr(68, None),
    'id': DXFAttr(69, None),
    'view_mode': DXFAttr(71, None),
    'circle_zoom': DXFAttr(72, None),
    'fast_zoom': DXFAttr(73, None),
    'ucs_icon': DXFAttr(74, None),
    'snap_on': DXFAttr(75, None),
    'grid_on': DXFAttr(76, None),
    'snap_style': DXFAttr(77, None),
    'snap_isopair': DXFAttr(78, None),
})


class Viewport(ac1009.Viewport):
    TEMPLATE = ClassifiedTags.from_text(_VPORTTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, vport_subclass)

_BLOCKRECORDTEMPLATE = """  0
BLOCK_RECORD
  5
0
330
0
100
AcDbSymbolTableRecord
100
AcDbBlockTableRecord
  2
BLOCK_RECORD_NAME
340
0
"""
blockrec_subclass = DefSubclass('AcDbBlockTableRecord', {
    'name': DXFAttr(2, None),
    'layout': DXFAttr(340, None),
})


class BlockRecord(GenericWrapper):
    """ Internal Object - use at your own risk!

    Required fields:
    owner: Soft-pointer ID/handle to owner object
    layout: Hard-pointer ID/handle to associated LAYOUT object
    """
    TEMPLATE = ClassifiedTags.from_text(_BLOCKRECORDTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, blockrec_subclass)
