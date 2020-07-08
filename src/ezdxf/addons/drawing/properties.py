# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union, List, Iterable, Sequence, Set
from ezdxf.lldxf import const
from ezdxf.addons.drawing.type_hints import Color, RGB
from ezdxf.addons import acadctb
from ezdxf.sections.table import table_key as layer_key
from ezdxf.tools.rgb import luminance

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, Layout, Table, Layer, Linetype, Drawing
    from ezdxf.entities.ltype import LinetypePattern

__all__ = [
    'Properties', 'LayerProperties', 'RenderContext', 'layer_key', 'rgb_to_hex', 'hex_to_rgb',
    'MODEL_SPACE_BG_COLOR', 'PAPER_SPACE_BG_COLOR', 'VIEWPORT_COLOR', 'CONTINUOUS_PATTERN',
]

MODEL_SPACE_BG_COLOR = '#212830'
PAPER_SPACE_BG_COLOR = '#ffffff'
VIEWPORT_COLOR = '#aaaaaa'  # arbitrary choice
CONTINUOUS_PATTERN = tuple()

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


def is_dark_color(color: Color) -> bool:
    luma = luminance(hex_to_rgb(color))
    return luma <= 0.2


class Properties:
    """ An implementation agnostic representation of entity properties like color and linetype.
    """

    def __init__(self):
        self.color: str = '#ffffff'  # format #RRGGBB or #RRGGBBAA
        # color names should be resolved into a actual color value

        # Store linetype name for backends which don't have the ability to use user-defined linetypes,
        # but have some predefined linetypes, maybe matching most common AutoCAD linetypes is possible
        self.linetype_name: str = 'CONTINUOUS'  # default linetype - store in UPPERCASE

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
        # SVG dash-pattern does not support points, so a minimal line length (maybe inferred from linewidth?)
        # has to be used, which alters# the overall line appearance a little bit - but linetype
        # mapping will never be perfect.
        # The continuous pattern is an empty tuple ()
        self.linetype_pattern: Tuple[float, ...] = CONTINUOUS_PATTERN
        self.linetype_scale: float = 1.0
        self.lineweight: float = 0.25  # line weight in mm, default lineweight 0.25?
        self.is_visible = True
        self.layer: str = '0'

    def __str__(self):
        return f'({self.color}, {self.linetype_name}, {self.lineweight}, {self.layer})'

    @property
    def rgb(self) -> RGB:
        """ Returns color as RGB tuple."""
        return hex_to_rgb(self.color[:7])  # ignore alpha if present

    @property
    def luminance(self) -> float:
        """ Returns perceived color luminance in range [0, 1] from dark to light. """
        return luminance(self.rgb)


class LayerProperties(Properties):
    def __init__(self):
        super().__init__()
        # LayerProperties.is_visible stores layer on/off state
        # LayerProperties.layer stores real layer name (mixed case)
        self.plot = True


DEFAULT_LAYER_PROPERTIES = LayerProperties()


class LayoutProperties:
    def __init__(self):
        self.name: str = 'Model'  # tab/display  name
        self._background_color: Color = MODEL_SPACE_BG_COLOR
        self._default_color: Color = '#ffffff'
        self._has_dark_background: bool = True

    @property
    def background_color(self) -> Color:
        return self._background_color

    @property
    def default_color(self) -> Color:
        return self._default_color

    @property
    def has_dark_background(self) -> bool:
        return self._has_dark_background

    def set_layout(self, layout: 'Layout', bg: Optional[Color] = None, fg: Optional[Color] = None) -> None:
        self.name = layout.name
        if bg is None:
            if self.name == 'Model':
                bg = MODEL_SPACE_BG_COLOR
            else:
                bg = PAPER_SPACE_BG_COLOR
        self.set_colors(bg, fg)

    def set_colors(self, bg: Color, fg: Color = None) -> None:
        self._background_color = bg
        self._has_dark_background = is_dark_color(bg)
        if fg is not None:
            self._default_color = fg
        else:
            self._default_color = '#ffffff' if self._has_dark_background else '#000000'


class RenderContext:
    def __init__(self, doc: Optional['Drawing'] = None, ctb: str = ''):
        self._saved_states: List[Properties] = []
        self.line_pattern = _load_line_pattern(doc.linetypes) if doc else dict()
        self.current_layout = LayoutProperties()  # default is 'Model'
        self.current_block: Optional[Properties] = None
        self.plot_styles = self._load_plot_style_table(ctb)
        # Always consider: entity layer may not exist
        # Layer name as key is normalized, most likely name.lower(), but may change in the future.
        self.layers: Dict[str, LayerProperties] = dict()
        if doc:
            for layer in doc.layers:  # type: Layer
                self.add_layer(layer)

    def add_layer(self, layer: 'Layer') -> None:
        properties = LayerProperties()
        name = layer_key(layer.dxf.name)
        properties.layer = layer.dxf.name  # store real layer name (mixed case)
        properties.color = self._true_layer_color(layer)
        properties.linetype_name = str(layer.dxf.linetype).upper()  # normalize linetype names
        properties.linetype_pattern = self.line_pattern.get(properties.linetype_name, CONTINUOUS_PATTERN)
        properties.lineweight = self._true_layer_lineweight(layer.dxf.lineweight)
        properties.is_visible = layer.is_on()
        properties.plot = bool(layer.dxf.plot)
        self.layers[name] = properties

    def _true_layer_color(self, layer: 'Layer') -> Color:
        if layer.dxf.hasattr('true_color'):
            return rgb_to_hex(layer.rgb)
        else:
            # Don't use layer.dxf.color: color < 0 is layer state off
            aci = layer.color
            # aci: 0=BYBLOCK, 256=BYLAYER, 257=BYOBJECT
            if aci < 1 or aci > 255:
                aci = 7  # default layer color
            return self._aci_to_true_color(aci)

    def _true_layer_lineweight(self, lineweight: int) -> float:
        if lineweight < 0:
            return self.default_lineweight()
        else:
            return float(lineweight) / 100.0

    @staticmethod
    def _load_plot_style_table(filename: str):
        # Each layout can have a different plot style table stored in Layout.dxf.current_style_sheet.
        # HEADER var $STYLESHEET stores the default ctb-file name
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

    def set_layers_state(self, layers: Set[str], state=True):
        """ Set layer state of `layers` to on/off.

        Args:
             layers: set of layer names
             state: `True` turn this `layers` on and others off,
                    `False` turn this `layers` off and others on
        """
        layers = {layer_key(name) for name in layers}
        for name, layer in self.layers.items():
            if name in layers:
                layer.is_visible = state
            else:
                layer.is_visible = not state

    def set_current_layout(self, layout: 'Layout'):
        self.current_layout.set_layout(layout)

    @property
    def is_block_context(self) -> bool:
        return bool(self.current_block)

    def push_state(self, block_reference: Properties) -> None:
        self._saved_states.append(self.current_block)
        self.current_block = block_reference

    def pop_state(self) -> None:
        self.current_block = self._saved_states.pop()

    def is_visible(self, entity: 'DXFGraphic') -> bool:
        if entity.dxf.invisible:
            return False
        layer_name = layer_key(entity.dxf.layer)
        layer = self.layers.get(layer_name)
        # todo: should we consider the plot flag too?
        if layer and not layer.is_visible:
            return False
        return True

    def resolve_all(self, entity: 'DXFGraphic') -> Properties:
        """ Resolve all properties for DXF `entity`. """
        p = Properties()
        p.color = self.resolve_color(entity)
        p.linetype_name, p.linetype_pattern = self.resolve_linetype(entity)
        p.lineweight = self.resolve_lineweight(entity)
        dxf = entity.dxf
        p.linetype_scale = dxf.ltscale
        p.is_visible = not bool(dxf.invisible)
        p.layer = dxf.layer
        layer_name = layer_key(p.layer)
        layer = self.layers.get(layer_name)
        if layer and p.is_visible:
            p.is_visible = layer.is_visible
        return p

    def resolve_color(self, entity: 'DXFGraphic', *, default_hatch_transparency: float = 0.8) -> Color:
        """ Resolve color of DXF `entity` """
        aci = entity.dxf.color  # defaults to BYLAYER
        if aci == const.BYLAYER:
            entity_layer = layer_key(entity.dxf.layer)
            # AutoCAD appears to treat layer 0 differently to other layers in this case.
            if self.is_block_context and entity_layer == '0':
                color = self.current_block.color
            else:
                color = self.layers.get(entity_layer, DEFAULT_LAYER_PROPERTIES).color

        elif aci == const.BYBLOCK:
            if not self.is_block_context:
                color = self.current_layout.default_color
            else:
                color = self.current_block.color

        else:  # BYOBJECT
            color = self._true_entity_color(entity.rgb, aci)

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
        elif 0 < aci < 256:
            return self._aci_to_true_color(aci)
        else:
            return self.current_layout.default_color  # unknown / invalid

    def _aci_to_true_color(self, aci: int) -> Color:
        if aci == 7:  # black/white; todo: bypasses plot style table
            if self.current_layout.has_dark_background:
                return '#ffffff'  # white
            else:
                return '#000000'  # black
        else:
            return rgb_to_hex(self.plot_styles[aci].color)

    def resolve_linetype(self, entity: 'DXFGraphic'):
        """ Resolve linetype of DXF `entity` """
        aci = entity.dxf.color
        # Not sure if plotstyle table overrides actual entity setting?
        if (0 < aci < 256) and self.plot_styles[aci].linetype != acadctb.OBJECT_LINETYPE:
            pass  # todo: return special line types  - overriding linetypes by plotstyle table
        name = entity.dxf.linetype.upper()  # default is 'BYLAYER'
        if name == 'BYLAYER':
            entity_layer = layer_key(entity.dxf.layer)

            # AutoCAD appears to treat layer 0 differently to other layers in this case.
            if self.is_block_context and entity_layer == '0':
                name = self.current_block.linetype_name
                pattern = self.current_block.linetype_pattern
            else:
                layer = self.layers.get(entity_layer, DEFAULT_LAYER_PROPERTIES)
                name = layer.linetype_name
                pattern = layer.linetype_pattern

        elif name == 'BYBLOCK':
            if self.is_block_context:
                name = self.current_block.linetype_name
                pattern = self.current_block.linetype_pattern
            else:
                # There is no default layout linetype
                name = 'STANDARD'
                pattern = CONTINUOUS_PATTERN
        else:
            pattern = self.line_pattern.get(name, CONTINUOUS_PATTERN)
        return name, pattern

    def resolve_lineweight(self, entity: 'DXFGraphic'):
        # Line weight in mm times 100 (e.g. 0.13mm = 13).
        # Smallest line weight is 0 and biggest line weight is 211
        # The DWG format is limited to a fixed value table: 0, 5, 9, ... 200, 211
        # DEFAULT: The LAYOUT entity has no explicit graphic properties.
        # BLOCK and BLOCK_RECORD entities also have no graphic properties.
        # Maybe XDATA or ExtensionDict in any of this entities.
        aci = entity.dxf.color
        # Not sure if plotstyle table overrides actual entity setting?
        if (0 < aci < 256) and self.plot_styles[aci].lineweight != acadctb.OBJECT_LINEWEIGHT:
            # overriding lineweight by plotstyle table
            return self.plot_styles.get_lineweight(aci)
        lineweight = entity.dxf.lineweight  # default is BYLAYER
        if lineweight == const.LINEWEIGHT_BYLAYER:
            entity_layer = layer_key(entity.dxf.layer)

            # AutoCAD appears to treat layer 0 differently to other layers in this case.
            if self.is_block_context and entity_layer == '0':
                return self.current_block.lineweight
            else:
                return self.layers.get(entity_layer, DEFAULT_LAYER_PROPERTIES).lineweight

        elif lineweight == const.LINEWEIGHT_BYBLOCK:
            if self.is_block_context:
                return self.current_block.lineweight
            else:
                # There is no default layout lineweight
                return self.default_lineweight()
        elif lineweight == const.LINEWEIGHT_DEFAULT:
            return self.default_lineweight()
        else:
            return float(lineweight) / 100.0

    def default_lineweight(self):
        return 0.25  # todo: ???


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


def _load_line_pattern(linetypes: 'Table') -> Dict[str, Tuple]:
    """ Load linetypes defined in a DXF document into  as dictionary,
    key is the upper case linetype name, value is the simplified line pattern,
    see compile_line_pattern().
    """
    pattern = dict()
    for linetype in linetypes:  # type: Linetype
        name = linetype.dxf.name.upper()
        pattern[name] = _compile_line_pattern_from_tags(linetype.pattern_tags)
    return pattern


def _merge_dashes(elements: Sequence[float]) -> Iterable[float]:
    """ Merge multiple consecutive lines, gaps or points into a single element. """

    def sign(v):
        if v < 0:
            return -1
        elif v > 0:
            return +1
        return 0

    buffer = elements[0]
    prev_sign = sign(buffer)
    for e in elements[1:]:
        if sign(e) == prev_sign:
            buffer += e
        else:
            yield buffer
            buffer = e
            prev_sign = sign(e)
    yield buffer


def _compile_line_pattern_from_tags(pattern: 'LinetypePattern') -> Tuple[float, ...]:
    """ Returns simplified dash-gap-dash... line pattern and dash is 0 for a point. """
    # complex line types with text and shapes are not supported
    if pattern.is_complex_type():
        return CONTINUOUS_PATTERN

    pattern_length = 0.0
    elements = []
    for tag in pattern.tags:
        if tag.code == 40:
            pattern_length = tag.value
        elif tag.code == 49:
            elements.append(tag.value)

    if len(elements) < 2:
        return CONTINUOUS_PATTERN
    return compile_line_pattern(pattern_length, elements)


def compile_line_pattern(total_length: float, elements: Sequence[float]) -> Tuple[float, ...]:
    """ Returns simplified dash-gap-dash... line pattern and dash is 0 for a point """
    elements = list(_merge_dashes(elements))
    if len(elements) < 2 or total_length <= 0.0:
        return CONTINUOUS_PATTERN

    sum_elements = sum(abs(e) for e in elements)
    if total_length > sum_elements:  # append a gap
        elements.append(sum_elements - total_length)

    if elements[0] < 0:  # start with a gap
        e = elements.pop(0)
        if elements[-1] < 0:  # extend last gap
            elements[-1] += e
        else:  # add last gap
            elements.append(e)
    # dash-gap-point
    # possible: dash-point or point-dash - just ignore yet
    # never: dash-dash or gap-gap or point-point
    return tuple(abs(e) for e in elements)
