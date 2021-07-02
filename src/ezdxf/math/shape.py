# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import Union, Iterable, List, TYPE_CHECKING
import math
from ezdxf.math import Vec2
from .construct2d import convex_hull_2d
from .offset2d import offset_vertices_2d
from .bbox import BoundingBox2d

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = ["Shape2d"]


class Shape2d:
    """2D geometry object as list of :class:`Vec2` objects, vertices can be
    moved, rotated and scaled.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects.

    """

    def __init__(self, vertices: Iterable["Vertex"] = None):
        self.vertices: List[Vec2] = (
            [] if vertices is None else Vec2.list(vertices)
        )

    @property
    def bounding_box(self) -> BoundingBox2d:
        """:class:`BoundingBox2d`"""
        return BoundingBox2d(self.vertices)

    def copy(self) -> "Shape2d":
        return self.__class__(self.vertices)

    __copy__ = copy

    def translate(self, vector: "Vertex") -> None:
        """Translate shape about `vector`."""
        delta = Vec2(vector)
        self.vertices = [v + delta for v in self.vertices]

    def scale(self, sx: float = 1.0, sy: float = 1.0) -> None:
        """Scale shape about `sx` in x-axis and `sy` in y-axis."""
        self.vertices = [Vec2((v.x * sx, v.y * sy)) for v in self.vertices]

    def scale_uniform(self, scale: float) -> None:
        """Scale shape uniform about `scale` in x- and y-axis."""
        self.vertices = [v * scale for v in self.vertices]

    def rotate(self, angle: float, center: "Vertex" = None) -> None:
        """Rotate shape around rotation `center` about `angle` in degrees."""
        self.rotate_rad(math.radians(angle), center)

    def rotate_rad(self, angle: float, center: "Vertex" = None) -> None:
        """Rotate shape around rotation `center` about `angle` in radians."""
        if center is not None:
            center = Vec2(center)
            self.translate(-center)  # faster than a Matrix44 multiplication
        self.vertices = [v.rotate(angle) for v in self.vertices]
        if center is not None:
            self.translate(center)  # faster than a Matrix44 multiplication

    def offset(self, offset: float, closed: bool = False) -> "Shape2d":
        """Returns a new offset shape, for more information see also
        :func:`ezdxf.math.offset_vertices_2d` function.

        Args:
            offset: line offset perpendicular to direction of shape segments
                defined by vertices order, offset > ``0`` is 'left' of line
                segment, offset < ``0`` is 'right' of line segment
            closed: ``True`` to handle as closed shape

        """
        return self.__class__(
            offset_vertices_2d(self.vertices, offset=offset, closed=closed)
        )

    def convex_hull(self) -> "Shape2d":
        """Returns convex hull as new shape."""
        return self.__class__(convex_hull_2d(self.vertices))

    # Sequence interface
    def __len__(self) -> int:
        """Returns `count` of vertices."""
        return len(self.vertices)

    def __getitem__(self, item: Union[int, slice]) -> Vec2:
        """Get vertex by index `item`, supports ``list`` like slicing."""
        return self.vertices[item]

    # limited List interface
    def append(self, vertex: "Vertex") -> None:
        """Append single `vertex`.

        Args:
             vertex: vertex as :class:`Vec2` compatible object

        """
        self.vertices.append(Vec2(vertex))

    def extend(self, vertices: Iterable) -> None:
        """Append multiple `vertices`.

        Args:
             vertices: iterable of vertices as :class:`Vec2` compatible objects

        """
        self.vertices.extend(Vec2.generate(vertices))
