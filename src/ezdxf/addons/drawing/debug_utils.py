from typing import List

from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.math import Vector


def draw_rect(points: List[Vector], color: Color, out: Backend):
    from ezdxf.addons.drawing import Properties

    props = Properties()
    props.color = color
    for a, b in zip(points, points[1:]):
        out.draw_line(a, b, props)
