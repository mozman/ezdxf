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


def set_current_layer(doc: "Drawing", layer_name: str):
    """Set current layer."""
    if layer_name not in doc.layers:
        raise const.DXFValueError(f'undefined layer name: "{layer_name}"')
    doc.header[CURRENT_LAYER] = layer_name


def set_current_color(doc: "Drawing", color: int):
    """Set current :ref:`ACI`."""
    if not validator.is_valid_aci_color(color):
        raise const.DXFValueError(f'invalid ACI color value: "{color}"')
    doc.header[CURRENT_COLOR] = color


def restore_wcs(doc: "Drawing"):
    """Restore the UCS settings in the HEADER section to the :ref:`WCS` and
    reset all current viewports to the WCS.
    """
    doc.header.reset_wcs()
    # TODO: reset viewports
