#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

from typing import TYPE_CHECKING, List
import math
from ezdxf.entities import factory
from ezdxf.math import Vector, UCS, NULLVEC

if TYPE_CHECKING:
    from ezdxf.entities import MLine, DXFGraphic


def virtual_entities(mline: 'MLine') -> List['DXFGraphic']:
    """ Yields 'virtual' parts of MLINE as LINE, ARC and HATCH entities.

    This entities are located at the original positions, but are not stored
    in the entity database, have no handle and are not assigned to any
    layout.
    """
    return []
