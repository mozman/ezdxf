# Created: 16.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Sequence
from ezdxf.dxfentity import DXFEntity
from ezdxf.lldxf.tags import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.validator import is_valid_layer_name
from ezdxf.lldxf.const import DXFInvalidLayerName, DXFValueError
from ezdxf.render.arrows import ARROWS
from ezdxf.algebra.ucs import UCS as UserCoordinateSystem

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFFactoryType

_LAYERTEMPLATE = """0
LAYER
5
0
2
LAYERNAME
70
0
62
7
6
CONTINUOUS
"""


# noinspection PyAugmentAssignment,PyUnresolvedReferences
class Layer(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LAYERTEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'name': DXFAttr(2),
        'flags': DXFAttr(70),
        'color': DXFAttr(62),  # dxf color index, if < 0 layer is off
        'linetype': DXFAttr(6),
    }))
    FROZEN = 0b00000001
    THAW = 0b11111110
    LOCK = 0b00000100
    UNLOCK = 0b11111011

    def post_new_hook(self) -> None:
        if not is_valid_layer_name(self.dxf.name):
            raise DXFInvalidLayerName("Invalid layer name '{}'".format(self.dxf.name))

    def is_frozen(self) -> bool:
        return self.dxf.flags & Layer.FROZEN > 0

    def freeze(self) -> None:
        self.dxf.flags = self.dxf.flags | Layer.FROZEN

    def thaw(self) -> None:
        self.dxf.flags = self.dxf.flags & Layer.THAW

    def is_locked(self) -> bool:
        return self.dxf.flags & Layer.LOCK > 0

    def lock(self) -> None:
        self.dxf.flags = self.dxf.flags | Layer.LOCK

    def unlock(self) -> None:
        self.dxf.flags = self.dxf.flags & Layer.UNLOCK

    def is_off(self) -> bool:
        return self.dxf.color < 0

    def is_on(self) -> bool:
        return not self.is_off()

    def on(self) -> None:
        self.dxf.color = abs(self.dxf.color)

    def off(self) -> None:
        self.dxf.color = -abs(self.dxf.color)

    def get_color(self) -> int:
        return abs(self.dxf.color)

    def set_color(self, color: int) -> None:
        color = abs(color) if self.is_on() else -abs(color)
        self.dxf.color = color


_STYLETEMPLATE = """0
STYLE
5
0
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
1.0
3
OpenSans-Regular.ttf
4

"""


class Style(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_STYLETEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'name': DXFAttr(2),
        'flags': DXFAttr(70),
        'height': DXFAttr(40),  # fixed height, 0 if not fixed
        'width': DXFAttr(41),  # width factor
        'oblique': DXFAttr(50),  # oblique angle in degree, 0 = vertical
        'generation_flags': DXFAttr(71),  # 2 = backward, 4 = mirrored in Y
        'last_height': DXFAttr(42),  # last height used
        'font': DXFAttr(3),  # primary font file name
        'bigfont': DXFAttr(4),  # big font name, blank if none
    }))

    def tk_font_tool(self):
        # initializes Tk(), therefore should only happen if font tools are really required.
        from ezdxf.tools.fonts import font
        return font(self.get_dxf_attrib('font', 'OpenSans-Regular.ttf'))


_LTYPETEMPLATE = """0
LTYPE
5
0
2
LTYPENAME
70
0
3
LTYPEDESCRIPTION
72
65
"""


class Linetype(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LTYPETEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'name': DXFAttr(2),
        'description': DXFAttr(3),
        'length': DXFAttr(40),
        'items': DXFAttr(73),
    }))

    @classmethod
    def new(cls, handle: str, dxfattribs: dict = None, dxffactory: 'DXFFactoryType' = None) -> DXFEntity:
        if dxfattribs is not None:
            pattern = dxfattribs.pop('pattern', [0.0])
            length = dxfattribs.pop('length', 0.)
        else:
            pattern = [0.0]
            length = 0.
        entity = super(Linetype, cls).new(handle, dxfattribs, dxffactory)
        entity._setup_pattern(pattern, length)
        return entity

    def _setup_pattern(self, pattern: Sequence[float], length: float) -> None:
        # length parameter is required for complex line types
        # pattern: [2.0, 1.25, -0.25, 0.25, -0.25] - 1. element is total pattern length
        # pattern elements: >0 line, <0 gap, =0 point
        self.tags.noclass.append(DXFTag(73, len(pattern) - 1))
        self.tags.noclass.append(DXFTag(40, float(pattern[0])))
        self.tags.noclass.extend((DXFTag(49, float(p)) for p in pattern[1:]))


_VPORTTEMPLATE = """0
VPORT
5
0
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


class VPort(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VPORTTEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
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
        # group code 69: 'id' is never saved in DXF, and DXF R13 and later has no group code 69
        'view_mode': DXFAttr(71),
        'circle_zoom': DXFAttr(72),
        'fast_zoom': DXFAttr(73),
        'ucs_icon': DXFAttr(74),
        'snap_on': DXFAttr(75),
        'grid_on': DXFAttr(76),
        'snap_style': DXFAttr(77),
        'snap_isopair': DXFAttr(78),
    }))


_UCSTEMPLATE = """0
UCS
5
0
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


class UCS(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_UCSTEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'name': DXFAttr(2),
        'flags': DXFAttr(70),
        'origin': DXFAttr(10, xtype=XType.point3d),
        'xaxis': DXFAttr(11, xtype=XType.point3d),
        'yaxis': DXFAttr(12, xtype=XType.point3d),
    }))

    def ucs(self) -> UserCoordinateSystem:
        return UserCoordinateSystem(
            origin=self.get_dxf_attrib('origin', default=(0, 0, 0)),
            ux=self.get_dxf_attrib('xaxis', default=(1, 0, 0)),
            uy=self.get_dxf_attrib('yaxis', default=(0, 1, 0)),
        )


_APPIDTEMPLATE = """0
APPID
5
0
2
APPNAME
70
0
"""


class AppID(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_APPIDTEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'name': DXFAttr(2),
        'flags': DXFAttr(70),
    }))


_VIEWTEMPLATE = """0
VIEW
5
0
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


class View(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VIEWTEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
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
    }))


_DIMSTYLETEMPLATE = """0
DIMSTYLE
105
0
2
DIMSTYLENAME
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
1.0
42
0.0
43
3.75
44
0.0
45
0.0
46
0.0
47
0.0
48
0.0
140
2.5
141
2.5
142
0.0
143
25.4
144
1.0
145
0.0
146
1.0
147
0.625
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


class DimStyle(DXFEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_DIMSTYLETEMPLATE)
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(105),
        'name': DXFAttr(2),
        'flags': DXFAttr(70),
        'dimpost': DXFAttr(3),
        'dimapost': DXFAttr(4),
        'dimblk': DXFAttr(5),
        'dimblk1': DXFAttr(6),
        'dimblk2': DXFAttr(7),
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
        'dimaltf': DXFAttr(143, default=1.),
        'dimlfac': DXFAttr(144),
        'dimtvp': DXFAttr(145),
        'dimtfac': DXFAttr(146),
        'dimgap': DXFAttr(147),
        'dimtol': DXFAttr(71),
        'dimlim': DXFAttr(72),
        'dimtih': DXFAttr(73),
        'dimtoh': DXFAttr(74),
        'dimse1': DXFAttr(75),
        'dimse2': DXFAttr(76),
        'dimtad': DXFAttr(77),  # 0 center, 1 above, 4 below dimline
        'dimzin': DXFAttr(78),
        'dimalt': DXFAttr(170),
        'dimaltd': DXFAttr(171),
        'dimtofl': DXFAttr(172),
        'dimsah': DXFAttr(173),
        'dimtix': DXFAttr(174),
        'dimsoxd': DXFAttr(175),
        'dimclrd': DXFAttr(176),
        'dimclre': DXFAttr(177),
        'dimclrt': DXFAttr(178),
    }))

    def print_attribs(self) -> None:
        attribs = [
            'dimpost', 'dimapost', 'dimblk', 'dimblk1', 'dimblk2', 'dimscale', 'dimasz', 'dimexo', 'dimdli',
            'dimexe', 'dimrnd', 'dimdle', 'dimtp', 'dimtm', 'dimtxt', 'dimcen', 'dimtsz', 'dimaltf', 'dimlfac',
            'dimtvp', 'dimtfac', 'dimgap', 'dimtol', 'dimlim', 'dimtih', 'dimtoh', 'dimse1', 'dimse2', 'dimtad',
            'dimzin', 'dimalt', 'dimaltd', 'dimtofl', 'dimsah', 'dimtix', 'dimsoxd', 'dimclrd', 'dimclre', 'dimclrt',
        ]
        for name in attribs:
            code = self.DXFATTRIBS[name].code
            value = self.get_dxf_attrib(name, None)
            print("{name} ({code}) = {value}".format(name=name, value=value, code=code))

    def set_blocks(self, blk: str = '', blk1: str = '', blk2: str = '') -> None:
        # Allplan sets '#' for dimblk if dimblk1 and dimblk2 is set
        self.set_dxf_attrib('dimblk', blk)
        self.set_dxf_attrib('dimblk1', blk1)
        self.set_dxf_attrib('dimblk2', blk2)

        # only existing BLOCK definitions allowed
        if self.drawing:
            blocks = self.drawing.blocks
            for b in (blk, blk1, blk2):
                if ARROWS.is_acad_arrow(b):  # not real blocks
                    continue
                if b and b not in blocks:
                    raise DXFValueError('BLOCK "{}" does not exist.'.format(blk))
