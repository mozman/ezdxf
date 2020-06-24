# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union, List
from pathlib import Path
from ezdxf.lldxf import const as DXFConstants
from ezdxf.addons.drawing.type_hints import Color, LayerName
from ezdxf.addons import acadctb

DEFAULT_CTB = 'color.ctb'
DEFAULT_MODEL_SPACE_BACKGROUND_COLOR = '#212830'
PAPER_SPACE_BACKGROUND_COLOR = '#ffffff'
VIEWPORT_COLOR = '#aaaaaa'  # arbitrary choice

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, Layout, Table, Layer

CONTINUOUS_PATTERN = (1.0,)

# color codes are 1-indexed so an additional entry was put in the 0th position
# different plot styles may choose different colors for the same code
# from ftp://ftp.ecn.purdue.edu/jshan/86/help/html/import_export/dxf_colortable.htm
# alternative color tables can be found at:
#  - http://www.temblast.com/songview/color3.htm
#  - http://gohtx.com/acadcolors.php

AUTOCAD_COLOR_INDEX = [
    None, '#ff0000', '#ffff00', '#00ff00', '#00ffff', '#0000ff', '#ff00ff', '#ffffff', '#808080', '#c0c0c0', '#ff0000',
    '#ff7f7f', '#a50000', '#a55252', '#7f0000', '#7f3f3f', '#4c0000', '#4c2626', '#260000', '#261313', '#ff3f00',
    '#ff9f7f', '#a52900', '#a56752', '#7f1f00', '#7f4f3f', '#4c1300', '#4c2f26', '#260900', '#261713', '#ff7f00',
    '#ffbf7f', '#a55200', '#a57c52', '#7f3f00', '#7f5f3f', '#4c2600', '#4c3926', '#261300', '#261c13', '#ffbf00',
    '#ffdf7f', '#a57c00', '#a59152', '#7f5f00', '#7f6f3f', '#4c3900', '#4c4226', '#261c00', '#262113', '#ffff00',
    '#ffff7f', '#a5a500', '#a5a552', '#7f7f00', '#7f7f3f', '#4c4c00', '#4c4c26', '#262600', '#262613', '#bfff00',
    '#dfff7f', '#7ca500', '#91a552', '#5f7f00', '#6f7f3f', '#394c00', '#424c26', '#1c2600', '#212613', '#7fff00',
    '#bfff7f', '#52a500', '#7ca552', '#3f7f00', '#5f7f3f', '#264c00', '#394c26', '#132600', '#1c2613', '#3fff00',
    '#9fff7f', '#29a500', '#67a552', '#1f7f00', '#4f7f3f', '#134c00', '#2f4c26', '#092600', '#172613', '#00ff00',
    '#7fff7f', '#00a500', '#52a552', '#007f00', '#3f7f3f', '#004c00', '#264c26', '#002600', '#132613', '#00ff3f',
    '#7fff9f', '#00a529', '#52a567', '#007f1f', '#3f7f4f', '#004c13', '#264c2f', '#002609', '#132617', '#00ff7f',
    '#7fffbf', '#00a552', '#52a57c', '#007f3f', '#3f7f5f', '#004c26', '#264c39', '#002613', '#13261c', '#00ffbf',
    '#7fffdf', '#00a57c', '#52a591', '#007f5f', '#3f7f6f', '#004c39',
    '#264c42', '#00261c', '#132621', '#00ffff', '#7fffff', '#00a5a5', '#52a5a5', '#007f7f', '#3f7f7f', '#004c4c',
    '#264c4c', '#002626', '#132626', '#00bfff', '#7fdfff', '#007ca5', '#5291a5', '#005f7f', '#3f6f7f', '#00394c',
    '#26424c', '#001c26', '#132126', '#007fff', '#7fbfff', '#0052a5', '#527ca5', '#003f7f', '#3f5f7f', '#00264c',
    '#26394c', '#001326', '#131c26', '#003fff', '#7f9fff', '#0029a5', '#5267a5', '#001f7f', '#3f4f7f', '#00134c',
    '#262f4c', '#000926', '#131726', '#0000ff', '#7f7fff', '#0000a5', '#5252a5', '#00007f', '#3f3f7f', '#00004c',
    '#26264c', '#000026', '#131326', '#3f00ff', '#9f7fff', '#2900a5', '#6752a5', '#1f007f', '#4f3f7f', '#13004c',
    '#2f264c', '#090026', '#171326', '#7f00ff', '#bf7fff', '#5200a5', '#7c52a5', '#3f007f', '#5f3f7f', '#26004c',
    '#39264c', '#130026', '#1c1326', '#bf00ff', '#df7fff', '#7c00a5', '#9152a5', '#5f007f', '#6f3f7f', '#39004c',
    '#42264c', '#1c0026', '#211326', '#ff00ff', '#ff7fff', '#a500a5', '#a552a5', '#7f007f', '#7f3f7f', '#4c004c',
    '#4c264c', '#260026', '#261326', '#ff00bf', '#ff7fdf', '#a5007c', '#a55291', '#7f005f', '#7f3f6f', '#4c0039',
    '#4c2642', '#26001c', '#261321', '#ff007f', '#ff7fbf', '#a50052', '#a5527c', '#7f003f', '#7f3f5f', '#4c0026',
    '#4c2639', '#260013', '#26131c', '#ff003f', '#ff7f9f', '#a50029', '#a55267', '#7f001f', '#7f3f4f', '#4c0013',
    '#4c262f', '#260009', '#261317', '#545454', '#767676', '#a0a0a0', '#c0c0c0', '#e0e0e0', '#000000'
]


class Properties:
    """ An implementation agnostic representation of entity properties like color and linetype.
    """

    def __init__(self):
        self.color: str = '#ffffff'  # format #RRGGBB or #RRGGBBAA
        # color names should be resolved into a actual color value

        # Store linetype name for backends which don't have the ability to use user-defined linetypes,
        # but have some predefined linetypes, maybe matching most common AutoCAD linetypes is possible
        self.linetype_name: str = 'CONTINUOUS'  # default linetype

        # Linetypes: Complex DXF linetypes are not supported:
        # 1. Don't know if there are any backends which can use linetypes including text or shapes
        # 2. No decoder for SHX files available, which are the source for shapes in linetypes
        # 3. SHX files are copyrighted - including in ezdxf not possible
        #
        # Simplified DXF linetype definition:
        # all line elements >= 0.0, 0.0 = point
        # all gap elements > 0.0
        # Usage as alternating line - gap sequence: line-gap-line-gap .... (line could be a point 0.0)
        # line-line or gap-gap - makes no sense
        # Examples:
        # DXF: ("DASHED", "Dashed __ __ __ __ __ __ __ __ __ __ __ __ __ _", [0.6, 0.5, -0.1])
        # first entry 0.6 is the total pattern length = sum(linetype_pattern)
        # linetype_pattern: [0.5, 0.1] = line-gap
        # DXF: ("DASHDOTX2", "Dash dot (2x) ____  .  ____  .  ____  .  ____", [2.4, 2.0, -0.2, 0.0, -0.2])
        # linetype_pattern: [2.0, 0.2, 0.0, 0.2] = line-gap-point-gap
        # Stored as tuple, so pattern could be used as key for caching.
        # SVG dash-pattern does not support points, so a minimal line length has to be used, which alters
        # the overall line appearance a little bit - but linetype mapping will never be perfect.
        self.linetype_pattern: Tuple[float, ...] = CONTINUOUS_PATTERN
        self.linetype_scale: float = 1.0
        self.lineweight: float = 0.13  # line weight in mm
        self.layer: str = '0'

    @classmethod
    def resolve(cls, entity: 'DXFGraphic', ctx: 'PropertyContext') -> 'Properties':
        p = cls()
        p.color = ctx.resolve_color(entity)
        p.linetype_name, p.linetype_pattern = ctx.resolve_linetype(entity)
        p.lineweight = ctx.resolve_lineweight(entity)
        p.linetype_scale = entity.dxf.ltscale
        p.layer = entity.dxf.layer
        return p

    def __str__(self):
        return f'({self.color}, {self.linetype_name}, {self.lineweight}, {self.layer})'


class LayerProperties(Properties):
    def __init__(self):
        super().__init__()
        self.is_on = True
        self.plot = True


class PropertyContext:
    def __init__(self, layout: 'Layout', ctb: str = DEFAULT_CTB):
        self._saved_states: List[Properties] = []
        self.plot_style_table = self._load_plot_style_table(ctb)
        self.layout_properties: Optional[Properties] = self._get_default_layout_properties(layout)
        self.block_reference_properties: Optional[Properties] = None
        self.layer_properties: Dict[LayerName, LayerProperties] = self._gather_layer_properties(layout.doc.layers)

    def _gather_layer_properties(self, layers: 'Table'):
        layer_table = {}
        for layer in layers:  # type: Layer
            properties = LayerProperties()
            name = self.layer_key(layer.dxf.name)
            properties.layer = name
            properties.color = self._true_layer_color(layer)
            properties.linetype = str(layer.dxf.linetype).upper()  # normalize linetype names
            properties.lineweight = self._true_layer_lineweight(layer.dxf.lineweight)
            properties.is_on = layer.is_on()
            properties.plot = bool(layer.dxf.plot)
            layer_table[name] = properties
        return layer_table

    @staticmethod
    def _load_plot_style_table(filename: str):
        # Each layout can have a different plot style table stored in Layout.dxf.current_style_sheet.
        # HEADER var $STYLESHEET stores the default ctb-file name
        try:
            ctb = acadctb.load(filename)
        except IOError:
            try:  # try setuptools to locate the default ctb-file:
                import pkg_resources
                filename = pkg_resources.resource_filename('ezdxf', f'addons/res/{DEFAULT_CTB}')
            except ImportError:  # or the old fashioned unsafe way
                filename = str(Path(__file__).parent/DEFAULT_CTB)
            try:
                ctb = acadctb.load(filename)
            except IOError:
                ctb = acadctb.new_ctb()

        # Colors in CTB files can be RGB colors but don't have to,
        # therefor initialize color without RGB values by the
        # default AutoCAD palette:
        for aci in range(1, 256):
            entry = ctb[aci]
            if entry.has_object_color():
                # initialize with default AutoCAD palette
                entry.color = hex_to_rgb(AUTOCAD_COLOR_INDEX[aci])
        return ctb

    def _get_default_layout_properties(self, layout: 'Layout') -> Properties:
        p = Properties()
        p.color = self.get_layout_default_color(layout)
        return p

    @staticmethod
    def get_layout_default_color(layout: 'Layout') -> Color:
        # todo: Get info from HEADER section?
        # The LAYOUT entity has no explicit graphic properties.
        # BLOCK and BLOCK_RECORD entities also have no graphic properties.
        # Maybe XDATA or ExtensionDict in any of this entities.
        return '#ffffff' if layout.is_modelspace else '#000000'

    @staticmethod
    def get_layout_background_color(layout: 'Layout') -> Color:
        # This values are managed by the CAD application, offer a method to set this value by user.
        return DEFAULT_MODEL_SPACE_BACKGROUND_COLOR if layout.is_modelspace else PAPER_SPACE_BACKGROUND_COLOR

    def _true_layer_color(self, layer: 'Layer') -> Color:
        return '#000000'  # todo

    def _true_layer_lineweight(self, lineweight: int) -> float:
        return 0.0  # todo

    @staticmethod
    def layer_key(name: str) -> str:
        # keep in sync with ezdxf.sections.LayerTable.key
        return name.lower()

    @property
    def block_reference_layer(self) -> str:
        return self.block_reference_properties.layer

    @property
    def is_block_reference_context(self) -> bool:
        return bool(self.block_reference_properties)

    def push_state(self, block_reference: Properties) -> None:
        self._saved_states.append(self.block_reference_properties)
        self.block_reference_properties = block_reference

    def pop_state(self) -> None:
        self.block_reference_properties = self._saved_states.pop()

    def resolve_color(self, entity: 'DXFGraphic', *, default_hatch_transparency: float = 0.8) -> Color:
        if not entity.dxf.hasattr('color'):
            return self.layout_properties.color  # unknown
        color_code = entity.dxf.color  # defaults to BYLAYER

        if color_code == DXFConstants.BYLAYER:
            entity_layer = self.layer_key(entity.dxf.layer)
            # AutoCAD appears to treat layer 0 differently to other layers in this case.
            if self.is_block_reference_context and entity_layer == '0':
                color = self.block_reference_properties.color
            else:
                color = self.layer_properties[entity_layer].color

        elif color_code == DXFConstants.BYBLOCK:
            if not self.is_block_reference_context:
                color = self.layout_properties.color
            else:
                color = self.block_reference_properties.color

        else:  # BYOBJECT
            color = self._true_entity_color(entity.rgb, color_code)

        if entity.dxftype() == 'HATCH':
            transparency = default_hatch_transparency
        else:
            transparency = entity.transparency

        alpha_float = 1.0 - transparency
        alpha = int(round(alpha_float * 255))
        if alpha == 255:
            return color
        else:
            return _rgba(color, alpha)

    def _true_entity_color(self,
                           true_color: Optional[Tuple[int, int, int]],
                           aci: int) -> Optional[Color]:  # AutoCAD Color Index
        if true_color is not None:
            return rgb_to_hex(true_color)
        # aci: 0=BYBLOCK, 256=BYLAYER, 257=BYOBJECT
        elif aci is not None and 0 < aci < 256:
            # plot style color format (r, g, b, mode) - todo: apply mode?
            return rgb_to_hex(self.plot_style_table[aci].color[:3])
        else:
            return self.layout_properties.color  # unknown / invalid

    def resolve_linetype(self, entity: 'DXFGraphic'):
        raise NotImplementedError

    def resolve_lineweight(self, entity: 'DXFGraphic'):
        # Line weight in mm times 100 (e.g. 0.13mm = 13).
        # Smallest line weight is 13 and biggest line weight is 211
        # The DWG format is limited to a fixed value table: ...
        # todo: BricsCAD offers smaller values (0.00, 0.05, 0.09), to be investigated!
        # -1 = BYLAYER
        # -2 = BYBLOCK
        # -3 = DEFAULT
        # DEFAULT: The LAYOUT entity has no explicit graphic properties.
        # BLOCK and BLOCK_RECORD entities also have no graphic properties.
        # Maybe XDATA or ExtensionDict in any of this entities.
        raise NotImplementedError


def rgb_to_hex(rgb: Union[Tuple[int, int, int], Tuple[float, float, float]]) -> Color:
    assert all(0 <= x <= 255 for x in rgb), f'invalid RGB color: {rgb}'
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def hex_to_rgb(hex_string: Color) -> Tuple[int, int, int]:
    hex_string = hex_string.lstrip('#')
    assert len(hex_string) == 6
    r = int(hex_string[0:2], 16)
    g = int(hex_string[2:4], 16)
    b = int(hex_string[4:6], 16)
    return r, g, b


def _rgba(color: Color, alpha: int) -> Color:
    """
    Args:
        color: may be an RGB or RGBA color
    """
    assert color.startswith('#') and len(color) in (7, 9), f'invalid RGB color: "{color}"'
    assert 0 <= alpha < 255, f'alpha out of range: {alpha}'
    return f'{color[:7]}{alpha:02x}'
