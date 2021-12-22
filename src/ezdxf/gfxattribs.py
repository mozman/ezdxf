#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Dict, Any
from ezdxf import colors
from ezdxf.lldxf import validator, const

__all__ = ["gfxattribs"]


def gfxattribs(
    *,
    layer: str = None,
    color: int = None,
    rgb: colors.RGB = None,
    linetype: str = None,
    lineweight: int = None,
    transparency: float = None,
) -> Dict[str, Any]:
    """
    Build a dictionary for often used DXF attributes of graphical entities.

    .. versionadded:: 0.18

    Args:
        layer: layer name as string
        color: :ref:`ACI` color value as integer
        rgb: RGB true color (red, green, blue) tuple, each channel value in the
            range from 0 to 255
        linetype: linetype name, does not check if the linetype exist!
        lineweight:  see :ref:`lineweights` documentation for valid values
        transparency: transparency value in the range from 0.0 to 1.0,
            where 0.0 is opaque and 1.0 if fully transparent

    Returns: DXF attribute dictionary

    Raises:
        DXFValueError: invalid attribute value

    """
    attribs: Dict[str, Any] = {}
    if layer is not None:
        if validator.is_valid_layer_name(layer):
            attribs["layer"] = layer
        else:
            raise const.DXFValueError(f"invalid layer name '{layer}'")
    if color is not None:
        if validator.is_valid_aci_color(color):
            attribs["color"] = color
        else:
            raise const.DXFValueError(f"invalid ACI color value '{color}'")
    if rgb is not None:
        if validator.is_valid_rgb(rgb):
            attribs["true_color"] = colors.rgb2int(rgb)
        else:
            raise const.DXFValueError(f"invalid true color value '{rgb}'")
    if linetype is not None:
        if validator.is_valid_table_name(linetype):
            attribs["linetype"] = linetype
        else:
            raise const.DXFValueError(f"invalid linetype name '{linetype}'")
    if lineweight is not None:
        if validator.is_valid_lineweight(lineweight):
            attribs["lineweight"] = lineweight
        else:
            raise const.DXFValueError(
                f"invalid lineweight value '{lineweight}'"
            )
    if transparency is not None:
        if isinstance(transparency, float) and (0.0 <= transparency <= 1.0):
            attribs["transparency"] = colors.float2transparency(transparency)
        else:
            raise const.DXFValueError(
                f"invalid transparency value '{transparency}'"
            )
    return attribs
