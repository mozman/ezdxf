#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Union, List

from ezdxf.addons.drawing import fonts
from ezdxf.entities import Text, Attrib
from ezdxf.lldxf import const
from ezdxf.render import Path
from ezdxf.tools import text

from matplotlib.path import Path as MPath

AnyText = Union[Text, Attrib]

# Each char consists of one or more paths!


def make_paths_from_entities(entity: AnyText) -> List[Path]:
    """ Convert text content from DXF entities TEXT, ATTRIB and ATTDEF into a
    list of :class:`~ezdxf.render.Path` objects. All paths in a single list.

    """
    return []


def make_paths_from_str(s: str,
                        font: fonts.Font,
                        halign: int = const.LEFT,
                        valign: int = const.BASELINE) -> List[Path]:
    """ Convert string `s` into a list of :class:`~ezdxf.render.Path` objects.
    All paths in a single list. The path objects
    are created for text height of one drawing unit as cap height (height of
    uppercase letter "X") and the insertion point is (0, 0). The paths  are
    aligned to this insertion point. BASELINE means the bottom of the
    letter "X".

    Note: These paths as easy and fast to transform,
      see :func:`~ezdxf.render.path.transform_paths`

    Args:
         s: text to convert
         font: font definition
         halign: horizontal alignment: LEFT=0, Center=1, RIGHT=2
         valign: vertical alignment: BASELINE=0, BOTTOM=1, MIDDLE=2, TOP=3

    """
    return []
