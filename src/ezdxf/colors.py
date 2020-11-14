#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import Tuple, Union
from ezdxf.tools.rgb import *  # ezdxf.colors will replace ezdxf.tools.rgb
from ezdxf.lldxf import const

RGB = Tuple[int, int, int]


# Flags for raw color int values:
# Take color from layer, ignore other bytes.
COLOR_TYPE_BY_LAYER = 0xc0
# Take color from insertion, ignore other bytes
COLOR_TYPE_BY_BLOCK = 0xc1
# RGB value, other bytes are R,G,B.
COLOR_TYPE_RGB = 0xc2
# ACI, AutoCAD color index, other bytes are 0,0,index ???
COLOR_TYPE_ACI = 0xc3

# Found in MLEADER text background color (group code 91) = -939524096
# guess: use window background color
COLOR_TYPE_WINDOW_BG = 0xc8


def decode_raw_color(value: int) -> Tuple[int, Union[int, RGB]]:
    """ Returns tuple(type, Union[aci, (r, g, b)]. """
    flags = (value >> 24) & 0xff
    if flags == COLOR_TYPE_BY_BLOCK:
        return COLOR_TYPE_BY_BLOCK, const.BYBLOCK
    elif flags == COLOR_TYPE_BY_LAYER:
        return COLOR_TYPE_BY_LAYER, const.BYLAYER
    elif flags == COLOR_TYPE_ACI:
        return COLOR_TYPE_ACI, value & 0xff
    elif flags == COLOR_TYPE_RGB:
        return COLOR_TYPE_RGB, int2rgb(value)
    elif flags == COLOR_TYPE_WINDOW_BG:
        return COLOR_TYPE_WINDOW_BG, 0
    else:
        raise ValueError(f'Unknown color type: 0x{flags:02x}')


BY_LAYER_RAW_VALUE = -1073741824  # -(-(0xc0 << 24) & 0xffffffff)
BY_BLOCK_RAW_VALUE = -1056964608  # -(-(0xc1 << 24) & 0xffffffff)


def encode_raw_color(value: Union[int, RGB]) -> int:
    if isinstance(value, int):
        if value == const.BYBLOCK:
            return BY_BLOCK_RAW_VALUE
        elif value == const.BYLAYER:
            return BY_LAYER_RAW_VALUE
        elif 0 < value < 256:
            return -(-(COLOR_TYPE_ACI << 24) & 0xffffffff) | value
        else:  # BYOBJECT (257) -> resolve to object color
            raise ValueError(f'Invalid color index: {value}')
    else:
        return -(-((COLOR_TYPE_RGB << 24) + rgb2int(value)) & 0xffffffff)


def float2transparency(value: float) -> int:
    """
    Returns DXF transparency value as integer in the range from 0 to 255,
    where 0 is 100% transparent and 255 is opaque.

    Args:
        value: transparency value as float in the range from 0 to 1, where 0 is
            opaque and 1 is 100% transparent.

    """
    return int((1. - float(value)) * 255) | 0x02000000


def transparency2float(value: int) -> float:
    """
    Returns transparency value as float from 0 to 1, 0 for no transparency
    (opaque) and 1 for 100% transparency.

    Args:
        value: DXF integer transparency value, 0 for 100% transparency and 255
            for opaque

    """
    # 255 -> 0.
    # 0 -> 1.
    return 1. - float(int(value) & 0xFF) / 255.
