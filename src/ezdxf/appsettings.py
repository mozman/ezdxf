#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
#  module to set application specific data
from typing import TYPE_CHECKING

from ezdxf.lldxf import const, validator

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing

CURRENT_LAYER = "$CLAYER"
CURRENT_COLOR = "$CECOLOR"
CURRENT_LINETYPE = "$CELTYPE"
CURRENT_LINEWEIGHT = "$CELWEIGHT"
CURRENT_LINETYPE_SCALE = "$CELTSCALE"
CURRENT_TEXTSTYLE = "$TEXTSTYLE"
CURRENT_DIMSTYLE = "$DIMSTYLE"


def set_current_layer(doc: "Drawing", name: str):
    """Set current layer."""
    if name not in doc.layers:
        raise const.DXFValueError(f'undefined layer: "{name}"')
    doc.header[CURRENT_LAYER] = name


def set_current_color(doc: "Drawing", color: int):
    """Set current :ref:`ACI`."""
    if not validator.is_valid_aci_color(color):
        raise const.DXFValueError(f'invalid ACI color value: "{color}"')
    doc.header[CURRENT_COLOR] = color


def set_current_linetype(doc: "Drawing", name: str):
    """Set current linetype."""
    if name not in doc.linetypes:
        raise const.DXFValueError(f'undefined linetype: "{name}"')
    doc.header[CURRENT_LINETYPE] = name


def set_current_lineweight(doc: "Drawing", lineweight: int):
    """Set current lineweight, see :ref:`lineweights` reference for valid
    values.
    """
    if not validator.is_valid_lineweight(lineweight):
        raise const.DXFValueError(f'invalid lineweight value: "{lineweight}"')
    doc.header[CURRENT_LINEWEIGHT] = lineweight


def set_current_linetype_scale(doc: "Drawing", scale: float):
    """Set current linetype scale.
    """
    if scale <= 0.0:
        raise const.DXFValueError(f'invalid linetype scale: "{scale}"')
    doc.header[CURRENT_LINETYPE_SCALE] = scale


def set_current_textstyle(doc: "Drawing", name: str):
    """Set current textstyle."""
    if name not in doc.styles:
        raise const.DXFValueError(f'undefined textstyle: "{name}"')
    doc.header[CURRENT_TEXTSTYLE] = name


def set_current_dimstyle(doc: "Drawing", name: str):
    """Set current dimstyle."""
    if name not in doc.dimstyles:
        raise const.DXFValueError(f'undefined dimstyle: "{name}"')
    doc.header[CURRENT_DIMSTYLE] = name


def restore_wcs(doc: "Drawing"):
    """Restore the UCS settings in the HEADER section to the :ref:`WCS` and
    reset all current viewports to the WCS.
    """
    doc.header.reset_wcs()
    # TODO: reset viewports
