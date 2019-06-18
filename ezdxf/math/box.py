from typing import List, Sequence, TYPE_CHECKING, Iterable, Tuple
import math
from .vector import Vec2
from .bbox import BoundingBox2d
from .line import ConstructionLine
from .construct2d import left_of_line, ConstructionTool

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class ConstructionBox(ConstructionTool):
    """
    Helper class to create rectangles.

    Args:
        center: center of rectangle
        width: width of rectangle
        height: height of rectangle
        angle: angle of rectangle in degrees

    """
    def __init__(self, center: 'Vertex' = (0, 0), width: float = 1, height: float = 1, angle: float = 0):
        self._center = Vec2(center)
        self._width = abs(width)  # type: float
        self._height = abs(height)  # type: float
        self._angle = angle  # type: float  # in degrees
        self._corners = None  # type: Tuple[Vec2, Vec2, Vec2, Vec2]
        self._tainted = True

    @classmethod
    def from_points(cls, p1: 'Vertex', p2: 'Vertex') -> 'ConstructionBox':
        """ Creates a :class:`ConstructionBox` from two opposite corners. """
        p1 = Vec2(p1)
        p2 = Vec2(p2)
        width = abs(p2.x - p1.x)
        height = abs(p2.y - p1.y)
        center = p1.lerp(p2)
        return cls(center=center, width=width, height=height)

    def update(self) -> None:
        if not self._tainted:
            return
        center = self.center
        w2 = Vec2.from_deg_angle(self._angle, self._width / 2.)
        h2 = Vec2.from_deg_angle(self._angle + 90, self._height / 2.)
        self._corners = (
            center - w2 - h2,  # lower left
            center + w2 - h2,  # lower right
            center + w2 + h2,  # upper right
            center - w2 + h2,  # upper left
        )
        self._tainted = False

    @property
    def bounding_box(self) -> BoundingBox2d:
        """ Returns :class:`BoundingBox2d`. """
        return BoundingBox2d(self.corners)

    @property
    def center(self) -> Vec2:
        """ center """
        return self._center

    @center.setter
    def center(self, c: 'Vertex') -> None:
        self._center = Vec2(c)
        self._tainted = True

    @property
    def width(self) -> float:
        """ width """
        return self._width

    @width.setter
    def width(self, w: float) -> None:
        self._width = abs(w)
        self._tainted = True

    @property
    def height(self) -> float:
        """ height """
        return self._height

    @height.setter
    def height(self, h: float) -> None:
        self._height = abs(h)
        self._tainted = True

    @property
    def incircle_radius(self) -> float:
        """ incircle radius """
        return min(self._width, self._height) / 2.

    @property
    def circumcircle_radius(self) -> float:
        """ circum circle radius"""
        return math.hypot(self._width, self._height) / 2.

    @property
    def angle(self) -> float:
        """ angle """
        return self._angle

    @angle.setter
    def angle(self, a: float) -> None:
        self._angle = a
        self._tainted = True

    @property
    def corners(self) -> Sequence[Vec2]:
        """ :class:`ConstructionBox` corners as sequence of 2d points. """
        self.update()
        return self._corners

    def __iter__(self) -> Iterable[Vec2]:
        """ Iterate over corners. """
        return iter(self.corners)

    def __getitem__(self, corner) -> Vec2:
        """ Get corner by index `corner`. """
        return self.corners[corner]

    def __repr__(self) -> str:
        return "ConstructionBox({0.center}, {0.width}, {0.height}, {0.angle})".format(self)

    def move(self, dx: float, dy: float) -> None:
        """
        Move :class:`ConstructionBox` about `dx` in x-axis and about `dy` in y-axis.

        Args:
            dx: translation in x-axis
            dy: translation in y-axis

        """
        self.center += Vec2((dx, dy))

    def expand(self, dw: float, dh: float) -> None:
        """ Expand :class:`ConstructionBox`. `dw` expand width, `dh` expand height. """
        self.width += dw
        self.height += dh

    def scale(self, sx: float, sy: float) -> None:
        """ Scale :class:`ConstructionBox`. """
        self.width *= sx
        self.height *= sy

    def rotate(self, angle: float) -> None:
        """ Rotate :class:`ConstructionBox`. """
        self.angle += angle

    def is_inside(self, point: 'Vertex') -> bool:
        """ Returns True if `point` is inside of :class:`ConstructionBox`. """
        point = Vec2(point)
        delta = self.center - point
        if math.isclose(self.angle, 0.):  # fast path for horizontal rectangles
            return abs(delta.x) <= (self._width / 2.) and abs(delta.y) <= (self._height / 2.)
        else:
            distance = delta.magnitude
            if distance > self.circumcircle_radius:
                return False
            elif distance <= self.incircle_radius:
                return True
            else:
                # inside if point is "left of line" of all border lines.
                p1, p2, p3, p4 = self.corners
                return all(
                    (left_of_line(point, a, b, online=True) for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)])
                )

    def is_any_corner_inside(self, other: 'ConstructionBox') -> bool:
        """ Returns True if any corner of `other` :class:`ConstructionBox` is inside this :class:`ConstructionBox`. """
        return any(self.is_inside(p) for p in other.corners)

    def is_overlapping(self, other: 'ConstructionBox') -> bool:
        """ Retruns True if `self` and `other` do overlap. """
        distance = (self.center - other.center).magnitude
        max_distance = self.circumcircle_radius + other.circumcircle_radius
        if distance > max_distance:
            return False
        min_distance = self.incircle_radius + other.incircle_radius
        if distance <= min_distance:
            return True

        if self.is_any_corner_inside(other):
            return True
        if other.is_any_corner_inside(self):
            return True
        # no corner inside of any box, maybe crossing boxes?
        # check intersection of diagonals
        c1, c2, c3, c4 = self.corners
        diag1 = ConstructionLine(c1, c3)
        diag2 = ConstructionLine(c2, c4)

        t1, t2, t3, t4 = other.corners
        test_diag = ConstructionLine(t1, t3)
        if test_diag.has_intersection(diag1) or test_diag.has_intersection(diag2):
            return True
        test_diag = ConstructionLine(t2, t4)
        if test_diag.has_intersection(diag1) or test_diag.has_intersection(diag2):
            return True

        return False

    def border_lines(self) -> Sequence[ConstructionLine]:
        """ Returns border lines of :class:`ConstructionBox` as sequence of :class:`ConstructionLine`. """
        p1, p2, p3, p4 = self.corners
        return (
            ConstructionLine(p1, p2),
            ConstructionLine(p2, p3),
            ConstructionLine(p3, p4),
            ConstructionLine(p4, p1),
        )

    def intersect(self, line: ConstructionLine) -> List[Vec2]:
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
