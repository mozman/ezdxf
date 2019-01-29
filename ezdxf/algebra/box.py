from typing import List, Sequence, TYPE_CHECKING
import math
from .vector import Vector
from .ray import ConstructionLine
from .base import left_of_line

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class ConstructionBox:
    def __init__(self, center: 'Vertex' = Vector(), width: float = 1, height: float = 1, angle: float = 0):
        self._center = Vector(center)
        self._width = abs(width)
        self._height = abs(height)
        self._angle = angle
        self._corners = None
        self._tainted = True

    @classmethod
    def from_points(cls, p1: 'Vertex', p2: 'Vertex'):
        p1 = Vector(p1)
        p2 = Vector(p2)
        width = abs(p2.x - p1.x)
        height = abs(p2.y - p1.y)
        center = p1.lerp(p2)
        return cls(center=center, width=width, height=height)

    def update(self):
        if not self._tainted:
            return
        center = self.center
        w2 = Vector.from_deg_angle(self._angle, self._width / 2.)
        h2 = Vector.from_deg_angle(self._angle + 90, self._height / 2.)
        self._corners = (
            center - w2 - h2,  # lower left
            center + w2 - h2,  # lower right
            center + w2 + h2,  # upper right
            center - w2 + h2,  # upper left
        )
        self._tainted = False

    @property
    def center(self) -> Vector:
        return self._center

    @center.setter
    def center(self, c: 'Vertex') -> None:
        self._center = Vector(c)
        self._tainted = True

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, w: float) -> None:
        self._width = abs(w)
        self._tainted = True

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, h: float) -> None:
        self._height = abs(h)
        self._tainted = True

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, a: float) -> None:
        self._angle = a
        self._tainted = True

    @property
    def corners(self) -> Sequence[Vector]:
        self.update()
        return self._corners

    def __getitem__(self, corner: int) -> Vector:
        return self.corners[corner]

    def __repr__(self) -> str:
        return "ConstructionBox({0.center}, {0.width}, {0.height}, {0.angle})".format(self)

    def move(self, dx: float, dy: float) -> None:
        self.center = self.center + (dx, dy)

    def expand(self, dw: float, dh: float) -> None:
        self.width += dw
        self.height += dh

    def scale(self, sx: float, sy: float) -> None:
        self.width *= sx
        self.height *= sy

    def rotate(self, angle: float) -> None:
        self.angle += angle

    def is_inside(self, point: 'Vertex') -> bool:
        if math.isclose(self.angle, 0.):  # fast path for horizontal rectangles
            delta = self.center - point
            return abs(delta.x) <= self._width/2 and abs(delta.y) <= self._height/2
        else:
            p1, p2, p3, p4 = self.corners
            point = Vector(point)
            return all(
                (left_of_line(point, a, b, online=True) for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)])
            )

    def border_lines(self) -> Sequence[ConstructionLine]:
        p1, p2, p3, p4 = self.corners
        return (
            ConstructionLine(p1, p2),
            ConstructionLine(p2, p3),
            ConstructionLine(p3, p4),
            ConstructionLine(p4, p1),
        )

    def intersect(self, line: ConstructionLine) -> List[Vector]:
        """
        Returns 0, 1 or 2 intersection points between `line` and `TextBox` border lines.

        Args:
            line: line to intersect with border lines

        Returns: list of intersection points

        """
        result = set()
        for border_line in self.border_lines():
            p = line.intersect(border_line)
            if p is not None:
                result.add(p)
        return sorted(result)
