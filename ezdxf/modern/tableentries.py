# Created: 16.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Union, cast
import logging
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType, VIRTUAL_TAG
from ezdxf.lldxf.const import DXFKeyError
from ezdxf.legacy import tableentries as legacy
from ezdxf.dxfentity import DXFEntity
from ezdxf.tools.complex_ltype import lin_compiler
from ezdxf.render.arrows import ARROWS

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, ComplexLineTypePart

_LAYERTEMPLATE = """0
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
    'handle': DXFAttr(5),
    'owner': DXFAttr(330),
})

symbol_subclass = DefSubclass('AcDbSymbolTableRecord', {})

layer_subclass = DefSubclass('AcDbLayerTableRecord', {
    'name': DXFAttr(2),  # layer name
    'flags': DXFAttr(70),
    'color': DXFAttr(62),  # dxf color index
    'linetype': DXFAttr(6),  # linetype name
    'plot': DXFAttr(290),  # don't plot this layer if 0 else 1
    'line_weight': DXFAttr(370),  # enum value???
    'lineweight': DXFAttr(370),  # enum value???
    'plot_style_name': DXFAttr(390),  # handle to PlotStyleName object
    'material': DXFAttr(347),  # handle to Material object
})


class Layer(legacy.Layer):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LAYERTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, layer_subclass)

    @classmethod
    def new(cls, handle: str, dxfattribs: dict = None, drawing: 'Drawing' = None) -> 'Layer':
        layer = super(Layer, cls).new(handle, dxfattribs, drawing)
        # just for testing scenarios where drawing is None
        if drawing is not None:
            layer.dxf.plot_style_name = drawing.rootdict['ACAD_PLOTSTYLENAME']
        return layer


_STYLETEMPLATE = """0
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
    'name': DXFAttr(2),
    'flags': DXFAttr(70),
    'height': DXFAttr(40),  # fixed height, 0 if not fixed
    'width': DXFAttr(41),  # width factor
    'oblique': DXFAttr(50),  # oblique angle in degree, 0 = vertical
    'generation_flags': DXFAttr(71),  # 2 = backward, 4 = mirrored in Y
    'last_height': DXFAttr(42),  # last height used
    'font': DXFAttr(3),  # primary font file name
    'bigfont': DXFAttr(4),  # big font name, blank if none
})


class Style(legacy.Style):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_STYLETEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, style_subclass)


_LTYPETEMPLATE = """0
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
    'name': DXFAttr(2),
    'description': DXFAttr(3),
    'length': DXFAttr(40),
    'items': DXFAttr(73),
})


class Linetype(legacy.Linetype):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LTYPETEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, linetype_subclass)

    def _setup_pattern(self, pattern: Union[Iterable[float], str], length: float) -> None:
        complex_line_type = True if isinstance(pattern, str) else False
        if complex_line_type:  # a .lin like line type definition string
            self._setup_complex_pattern(pattern, length)
        else:
            # pattern: [2.0, 1.25, -0.25, 0.25, -0.25] - 1. element is total pattern length
            # pattern elements: >0 line, <0 gap, =0 point
            subclass = self.tags.get_subclass('AcDbLinetypeTableRecord')
            subclass.append(DXFTag(73, len(pattern) - 1))
            subclass.append(DXFTag(40, float(pattern[0])))
            for element in pattern[1:]:
                subclass.append(DXFTag(49, float(element)))
                subclass.append(DXFTag(74, 0))

    def _setup_complex_pattern(self, pattern: str, length: float) -> None:
        tokens = lin_compiler(pattern)
        subclass = self.tags.get_subclass('AcDbLinetypeTableRecord')
        subclass.append(DXFTag(73, 0))  # temp length of 0
        subclass.append(DXFTag(40, length))
        count = 0
        for token in tokens:
            if isinstance(token, DXFTag):
                if subclass[-1].code == 49:  # useless 74 only after 49 :))
                    subclass.append(DXFTag(74, 0))
                subclass.append(token)
                count += 1
            else:  # TEXT or SHAPE
                tags = cast('ComplexLineTypePart', token).complex_ltype_tags(self.drawing)
                subclass.extend(tags)
        subclass.append(DXFTag(74, 0))  # useless 74 at the end :))
        subclass.update(DXFTag(73, count))


_APPIDTEMPLATE = """0
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
    'name': DXFAttr(2),
    'flags': DXFAttr(70),
})


class AppID(legacy.AppID):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_APPIDTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, appid_subclass)


_DIMSTYLETEMPLATE = """0
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
    'handle': DXFAttr(105),
    'owner': DXFAttr(330),
})

dimstyle_subclass = DefSubclass('AcDbDimStyleTableRecord', {
    'name': DXFAttr(2),
    'flags': DXFAttr(70),
    'dimpost': DXFAttr(3),
    'dimapost': DXFAttr(4),
    'dimblk': DXFAttr(5),  # obsolete
    'dimblk1': DXFAttr(6),  # obsolete
    'dimblk2': DXFAttr(7),  # obsolete
    'dimscale': DXFAttr(40),
    'dimasz': DXFAttr(41),
    'dimexo': DXFAttr(42),
    'dimdli': DXFAttr(43),
    'dimexe': DXFAttr(44),
    'dimrnd': DXFAttr(45),
    'dimdle': DXFAttr(46),
    'dimtp': DXFAttr(47),
    'dimtm': DXFAttr(48),
    'dimtxt': DXFAttr(140),
    'dimcen': DXFAttr(141),
    'dimtsz': DXFAttr(142),
    'dimaltf': DXFAttr(143),
    'dimlfac': DXFAttr(144),
    'dimtvp': DXFAttr(145),
    'dimtfac': DXFAttr(146),
    'dimgap': DXFAttr(147),
    'dimaltrnd': DXFAttr(148),
    'dimtol': DXFAttr(71),
    'dimlim': DXFAttr(72),
    'dimtih': DXFAttr(73),
    'dimtoh': DXFAttr(74),
    'dimse1': DXFAttr(75),
    'dimse2': DXFAttr(76),
    'dimtad': DXFAttr(77),
    'dimzin': DXFAttr(78),
    'dimazin': DXFAttr(79),
    'dimalt': DXFAttr(170),
    'dimaltd': DXFAttr(171),
    'dimtofl': DXFAttr(172),
    'dimsah': DXFAttr(173),
    'dimtix': DXFAttr(174),
    'dimsoxd': DXFAttr(175),
    'dimclrd': DXFAttr(176),
    'dimclre': DXFAttr(177),
    'dimclrt': DXFAttr(178),
    'dimadec': DXFAttr(179),
    'dimunit': DXFAttr(270),
    'dimdec': DXFAttr(271),
    'dimtdec': DXFAttr(272),
    'dimaltu': DXFAttr(273),
    'dimalttd': DXFAttr(274),
    'dimaunit': DXFAttr(275),
    'dimfrac': DXFAttr(276),
    'dimlunit': DXFAttr(277),
    'dimdsep': DXFAttr(278),
    'dimtmove': DXFAttr(279),
    'dimjust': DXFAttr(280),
    'dimsd1': DXFAttr(281),
    'dimsd2': DXFAttr(282),
    'dimtolj': DXFAttr(283),
    'dimtzin': DXFAttr(284),
    'dimaltz': DXFAttr(285),
    'dimalttz': DXFAttr(286),
    'dimfit': DXFAttr(287),  # obsolete, now use DIMATFIT and DIMTMOVE
    'dimupt': DXFAttr(288),
    'dimatfit': DXFAttr(289),
    'dimtxsty_handle': DXFAttr(340),  # handle of referenced STYLE entry
    # virtual DXF attribute 'dimtxsty': set/get referenced STYLE by name as callback
    'dimtxsty': DXFAttr(VIRTUAL_TAG, xtype=XType.callback, getter='get_text_style', setter='set_text_style'),
    # virtual DXF attribute 'dimldrblk': set/get referenced STYLE by name as callback
    'dimldrblk': DXFAttr(VIRTUAL_TAG, xtype=XType.callback, getter='get_leader_block_name',
                         setter='set_leader_block_name'),
    'dimldrblk_handle': DXFAttr(341),  # handle of referenced BLOCK_RECORD
    'dimblk_handle': DXFAttr(342),  # handle of referenced BLOCK_RECORD
    'dimblk1_handle': DXFAttr(343),  # handle of referenced BLOCK_RECORD
    'dimblk2_handle': DXFAttr(344),  # handle of referenced BLOCK_RECORD
    'dimlwd': DXFAttr(371),  # lineweight enum value
    'dimlwe': DXFAttr(372),  # lineweight enum value
})


class DimStyle(legacy.DimStyle):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_DIMSTYLETEMPLATE)
    DXFATTRIBS = DXFAttributes(handle105_subclass, symbol_subclass, dimstyle_subclass)
    CODE_TO_DXF_ATTRIB = dict(DXFATTRIBS.build_group_code_items(legacy.dim_filter))

    def _set_blk_handle(self, attr: str, arrow_name: str) -> None:
        if arrow_name == ARROWS.closed_filled:
            # special arrow, no handle needed (is '0' if set)
            # do not create block by default, this will be done if arrow is used
            # and block record handle is not needed here
            self.del_dxf_attrib(attr)
            return

        blocks = self.drawing.blocks
        if ARROWS.is_acad_arrow(arrow_name):
            # create block, because need block record handle is needed here
            block_name = ARROWS.create_block(blocks, arrow_name)
        else:
            block_name = arrow_name

        blk = blocks.get(block_name)
        self.set_dxf_attrib(attr, blk.block_record_handle)

    def set_arrows(self, blk: str = '', blk1: str = '', blk2: str = '') -> None:
        if self.dxfversion > 'AC1009':
            self._set_blk_handle('dimblk_handle', blk)
            self._set_blk_handle('dimblk1_handle', blk1)
            self._set_blk_handle('dimblk2_handle', blk2)
        else:
            # set arrows by arrow name
            super().set_arrows(blk, blk1, blk2)

    def get_text_style(self) -> str:
        handle = self.get_dxf_attrib('dimtxsty_handle', None)
        if handle:
            return get_text_style_by_handle(handle, self.drawing)
        else:
            logging.warning('DIMSTYLE "{}": text style handle not set.'.format(self.dxf.name))
            return 'STANARD'

    def set_text_style(self, name: str) -> None:
        style = self.drawing.styles.get(name)
        self.set_dxf_attrib('dimtxsty_handle', style.dxf.handle)

    def get_leader_block_name(self) -> str:
        handle = self.get_dxf_attrib('dimldrblk_handle', None)
        if handle in (None, '0'):
            # unset handle or handle '0' is default closed filled arrow
            return ARROWS.closed_filled
        else:
            block_name = get_block_name_by_handle(handle, self.drawing)
            return ARROWS.arrow_name(block_name)  # if arrow return standard arrow name else just the block name

    def set_leader_block_name(self, name) -> None:
        self._set_blk_handle('dimldrblk_handle', name)


def get_text_style_by_handle(handle, drawing: 'Drawing', default='STANDARD') -> str:
    try:
        entry = drawing.get_dxf_entity(handle)
    except DXFKeyError:
        logging.warning('Invalid text style handle "{}".'.format(handle))
        text_style_name = default
    else:
        text_style_name = entry.dxf.name
    return text_style_name


def get_block_name_by_handle(handle, drawing: 'Drawing', default='') -> str:
    try:
        entry = drawing.get_dxf_entity(handle)
    except DXFKeyError:
        block_name = default
    else:
        block_name = entry.dxf.name
    return block_name


_UCSTEMPLATE = """0
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
    'name': DXFAttr(2),
    'flags': DXFAttr(70),
    'origin': DXFAttr(10, xtype=XType.point3d),
    'xaxis': DXFAttr(11, xtype=XType.point3d),
    'yaxis': DXFAttr(12, xtype=XType.point3d),
})


class UCS(legacy.UCS):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_UCSTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, ucs_subclass)


_VIEWTEMPLATE = """0
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
    'name': DXFAttr(2),
    'flags': DXFAttr(70),
    'height': DXFAttr(40),
    'width': DXFAttr(41),
    'center_point': DXFAttr(10, xtype=XType.point2d),
    'direction_point': DXFAttr(11, xtype=XType.point3d),
    'target_point': DXFAttr(12, xtype=XType.point3d),
    'lens_length': DXFAttr(42),
    'front_clipping': DXFAttr(43),
    'back_clipping': DXFAttr(44),
    'view_twist': DXFAttr(50),
    'view_mode': DXFAttr(71),
})


class View(legacy.View):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VIEWTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, view_subclass)


_VPORTTEMPLATE = """0
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
    'name': DXFAttr(2),
    'flags': DXFAttr(70),
    'lower_left': DXFAttr(10, xtype=XType.point2d),
    'upper_right': DXFAttr(11, xtype=XType.point2d),
    'center_point': DXFAttr(12, xtype=XType.point2d),
    'snap_base': DXFAttr(13, xtype=XType.point2d),
    'snap_spacing': DXFAttr(14, xtype=XType.point2d),
    'grid_spacing': DXFAttr(15, xtype=XType.point2d),
    'direction_point': DXFAttr(16, xtype=XType.point3d),
    'target_point': DXFAttr(17, xtype=XType.point3d),
    'height': DXFAttr(40),
    'aspect_ratio': DXFAttr(41),
    'lens_length': DXFAttr(42),
    'front_clipping': DXFAttr(43),
    'back_clipping': DXFAttr(44),
    'snap_rotation': DXFAttr(50),
    'view_twist': DXFAttr(51),
    'status': DXFAttr(68),
    'view_mode': DXFAttr(71),
    'circle_zoom': DXFAttr(72),
    'fast_zoom': DXFAttr(73),
    'ucs_icon': DXFAttr(74),
    'snap_on': DXFAttr(75),
    'grid_on': DXFAttr(76),
    'snap_style': DXFAttr(77),
    'snap_isopair': DXFAttr(78),
})


class VPort(legacy.VPort):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VPORTTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, vport_subclass)


_BLOCKRECORDTEMPLATE = """0
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
    'name': DXFAttr(2),
    'layout': DXFAttr(340),
})


class BlockRecord(DXFEntity):
    """ Internal Object - use at your own risk!

    Required fields:
    owner: Soft-pointer ID/handle to owner object
    layout: Hard-pointer ID/handle to associated LAYOUT object - is '0' if block definition
    """
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_BLOCKRECORDTEMPLATE)
    DXFATTRIBS = DXFAttributes(none_subclass, symbol_subclass, blockrec_subclass)
