# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from typing import Dict, Optional, Tuple, Union, List

from ezdxf import entities as DXFEntity
from ezdxf.addons.drawing.type_hints import Color, LayerName
from ezdxf.entities import DXFGraphic
from ezdxf.layouts import Layout
from ezdxf.lldxf import const as DXFConstants

DEFAULT_MODEL_SPACE_BACKGROUND_COLOR = '#212830'
VIEWPORT_COLOR = '#aaaaaa'  # arbitrary choice
# color codes are 1-indexed so an additional entry was put in the 0th position
# different plot styles may choose different colors for the same code
# from ftp://ftp.ecn.purdue.edu/jshan/86/help/html/import_export/dxf_colortable.htm
# alternative color tables can be found at:
#  - http://www.temblast.com/songview/color3.htm
#  - http://gohtx.com/acadcolors.php
AUTOCAD_COLOR_INDEX = [None, '#ff0000', '#ffff00', '#00ff00', '#00ffff', '#0000ff', '#ff00ff', '#ffffff', '#808080', '#c0c0c0', '#ff0000', '#ff7f7f', '#a50000', '#a55252', '#7f0000', '#7f3f3f', '#4c0000', '#4c2626', '#260000', '#261313', '#ff3f00', '#ff9f7f', '#a52900', '#a56752', '#7f1f00', '#7f4f3f', '#4c1300', '#4c2f26', '#260900', '#261713', '#ff7f00', '#ffbf7f', '#a55200', '#a57c52', '#7f3f00', '#7f5f3f', '#4c2600', '#4c3926', '#261300', '#261c13', '#ffbf00', '#ffdf7f', '#a57c00', '#a59152', '#7f5f00', '#7f6f3f', '#4c3900', '#4c4226', '#261c00', '#262113', '#ffff00', '#ffff7f', '#a5a500', '#a5a552', '#7f7f00', '#7f7f3f', '#4c4c00', '#4c4c26', '#262600', '#262613', '#bfff00', '#dfff7f', '#7ca500', '#91a552', '#5f7f00', '#6f7f3f', '#394c00', '#424c26', '#1c2600', '#212613', '#7fff00', '#bfff7f', '#52a500', '#7ca552', '#3f7f00', '#5f7f3f', '#264c00', '#394c26', '#132600', '#1c2613', '#3fff00', '#9fff7f', '#29a500', '#67a552', '#1f7f00', '#4f7f3f', '#134c00', '#2f4c26', '#092600', '#172613', '#00ff00', '#7fff7f', '#00a500', '#52a552', '#007f00', '#3f7f3f', '#004c00', '#264c26', '#002600', '#132613', '#00ff3f', '#7fff9f', '#00a529', '#52a567', '#007f1f', '#3f7f4f', '#004c13', '#264c2f', '#002609', '#132617', '#00ff7f', '#7fffbf', '#00a552', '#52a57c', '#007f3f', '#3f7f5f', '#004c26', '#264c39', '#002613', '#13261c', '#00ffbf', '#7fffdf', '#00a57c', '#52a591', '#007f5f', '#3f7f6f', '#004c39',
                       '#264c42', '#00261c', '#132621', '#00ffff', '#7fffff', '#00a5a5', '#52a5a5', '#007f7f', '#3f7f7f', '#004c4c', '#264c4c', '#002626', '#132626', '#00bfff', '#7fdfff', '#007ca5', '#5291a5', '#005f7f', '#3f6f7f', '#00394c', '#26424c', '#001c26', '#132126', '#007fff', '#7fbfff', '#0052a5', '#527ca5', '#003f7f', '#3f5f7f', '#00264c', '#26394c', '#001326', '#131c26', '#003fff', '#7f9fff', '#0029a5', '#5267a5', '#001f7f', '#3f4f7f', '#00134c', '#262f4c', '#000926', '#131726', '#0000ff', '#7f7fff', '#0000a5', '#5252a5', '#00007f', '#3f3f7f', '#00004c', '#26264c', '#000026', '#131326', '#3f00ff', '#9f7fff', '#2900a5', '#6752a5', '#1f007f', '#4f3f7f', '#13004c', '#2f264c', '#090026', '#171326', '#7f00ff', '#bf7fff', '#5200a5', '#7c52a5', '#3f007f', '#5f3f7f', '#26004c', '#39264c', '#130026', '#1c1326', '#bf00ff', '#df7fff', '#7c00a5', '#9152a5', '#5f007f', '#6f3f7f', '#39004c', '#42264c', '#1c0026', '#211326', '#ff00ff', '#ff7fff', '#a500a5', '#a552a5', '#7f007f', '#7f3f7f', '#4c004c', '#4c264c', '#260026', '#261326', '#ff00bf', '#ff7fdf', '#a5007c', '#a55291', '#7f005f', '#7f3f6f', '#4c0039', '#4c2642', '#26001c', '#261321', '#ff007f', '#ff7fbf', '#a50052', '#a5527c', '#7f003f', '#7f3f5f', '#4c0026', '#4c2639', '#260013', '#26131c', '#ff003f', '#ff7f9f', '#a50029', '#a55267', '#7f001f', '#7f3f4f', '#4c0013', '#4c262f', '#260009', '#261317', '#545454', '#767676', '#a0a0a0', '#c0c0c0', '#e0e0e0', '#000000']


class ColorContext:
    """
    Attributes:
        layout_default_color: white when in modelspace and black when in paperspace
    """
    def __init__(self, layout: Layout, color_index: Optional[List[Color]] = None):
        self._block_color: Optional[Color] = None
        self._insert_layer: Optional[LayerName] = None
        self._saved_states = []
        self.color_index = color_index or AUTOCAD_COLOR_INDEX
        self.layout_default_color: Optional[Color] = self.get_layout_default_color(layout)
        self.layer_colors: Dict[LayerName, Color] = \
            {name.lower(): self.get_layer_color(layer) for name, layer in layout.doc.layers.entries.items()}

    @property
    def insert_layer(self) -> Optional[LayerName]:
        return self._insert_layer

    def push_state(self, block_color: Color, insert_layer: LayerName) -> None:
        self._saved_states.append((self._block_color, self._insert_layer))
        self._block_color = block_color
        self._insert_layer = insert_layer

    def pop_state(self) -> None:
        self._block_color, self._insert_layer = self._saved_states.pop()

    def get_entity_color(self, entity: DXFGraphic, *, default_hatch_transparency: float = 0.8) -> Color:
        color_code = entity.dxf.color  # defaults to BYLAYER

        if color_code == DXFConstants.BYLAYER:
            entity_layer = entity.dxf.layer.lower()
            # AutoCAD appears to treat layer 0 differently to other layers in this case.
            if self._insert_layer is not None and entity_layer == '0':
                color = self.layer_colors[self._insert_layer]
            else:
                color = self.layer_colors[entity_layer]

        elif color_code == DXFConstants.BYBLOCK:
            if self._block_color is None:
                color = self.layout_default_color
            else:
                color = self._block_color

        else:  # BYOBJECT
            color = self._get_color(entity.rgb, color_code)

        if isinstance(entity, DXFEntity.Hatch):
            transparency = default_hatch_transparency
        else:
            transparency = entity.transparency

        alpha_float = 1.0 - transparency
        alpha = int(round(alpha_float * 255))
        if alpha == 255:
            return color
        else:
            return _rgba(color, alpha)

    def get_layer_color(self, layer: DXFEntity.Layer) -> Color:
        color = self._get_color(layer.rgb, layer.color)
        return color if color is not None else self.layout_default_color

    @staticmethod
    def get_layout_default_color(layout: Layout) -> Color:
        return '#ffffff' if layout.is_modelspace else '#000000'

    @staticmethod
    def get_layout_background_color(layout: Layout) -> Color:
        return DEFAULT_MODEL_SPACE_BACKGROUND_COLOR if layout.is_modelspace else '#ffffff'

    def _get_color(self,
                   maybe_true_color: Optional[Tuple[int, int, int]],
                   color_code: int) -> Optional[Color]:
        if maybe_true_color is not None:
            return rgb_to_hex(maybe_true_color)
        elif color_code is not None and 0 < color_code < len(self.color_index):  # 0 is not a valid color code
            return self.color_index[color_code]
        else:
            return self.layout_default_color  # unknown / invalid


def get_layer_color(layer: DXFEntity.Layer, color_index: Optional[List[str]] = None) -> Optional[Color]:
    color_index = color_index or AUTOCAD_COLOR_INDEX
    if layer.rgb is not None:
        return rgb_to_hex(layer.rgb)
    elif layer.color is not None and 0 < layer.color < len(color_index):  # 0 is not a valid color code
        return color_index[layer.color]
    else:
        return None  # unknown / invalid


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
