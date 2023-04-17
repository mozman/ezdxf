#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Iterator, TYPE_CHECKING, Optional
import math

# The pure Python implementation can't import from ._ctypes or ezdxf.math!
from ._vector import Vec2
# from ezdxf.math import Vec2

if TYPE_CHECKING:
    from ezdxf.math import UVec

__all__ = ["Matrix33"]


def floats(items: Iterable) -> tuple[float, ...]:
    return tuple(float(v) for v in items)


class Matrix33:
    """An immutable 3x3 `transformation matrix`_ optimized for 2D graphic.

    The utility functions for constructing transformations and transforming
    vectors and points assumes that vectors are stored as row vectors, meaning
    when multiplied, transformations are applied left to right (e.g. vAB
    transforms v by A then by B).

    Args:
        values: ``None`` for the identity matrix or an iterable of 9 floats

    .. _transformation matrix: https://en.wikipedia.org/wiki/Transformation_matrix
    """

    _identity = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    __slots__ = ("_matrix",)

    def __init__(self, values: Optional[Iterable[float]] = None) -> None:
        self._matrix: tuple[float, ...]
        if values is None:
            self._matrix = Matrix33._identity
        else:
            self._matrix = floats(values)
        if len(self._matrix) != 9:
            raise ValueError(f"expected 9 floats, got {len(self._matrix)}")

    def __iter__(self) -> Iterator[float]:
        return iter(self._matrix)

    def __repr__(self) -> str:
        """Returns the representation string of the matrix:
        ``Matrix44((col0, col1, col2, col3), (...), (...), (...))``
        """

        def format_row(row):
            return "(%s)" % ", ".join(str(value) for value in row)

        return "Matrix44(%s)" % ", ".join(
            (
                format_row(self._matrix[0:3]),
                format_row(self._matrix[3:6]),
                format_row(self._matrix[6:9]),
            )
        )

    def isclose(self, m: Matrix33, abs_tol=1e-12) -> bool:
        return all(
            math.isclose(v1, v2, abs_tol=abs_tol)
            for v1, v2 in zip(self._matrix, m._matrix)
        )

    @classmethod
    def translate(cls, dx: float, dy: float) -> Matrix33:
        """Returns a translation matrix for translation vector (dx, dy)."""
        m = cls()
        m._matrix = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, float(dx), float(dy), 1.0)
        return m

    def transform(self, vector: UVec) -> Vec2:
        """Returns a transformed vertex."""
        m = self._matrix
        x, y = Vec2(vector)
        return Vec2(x * m[0] + y * m[3] + m[6], x * m[1] + y * m[4] + m[7])

    def transform_vertices(self, vertices: Iterable[UVec]) -> Iterable[Vec2]:
        """Returns an iterable of transformed vertices."""
        (m0, m1, m2, m3, m4, m5, m6, m7, m8) = self._matrix
        for vertex in vertices:
            x, y = Vec2(vertex)
            yield Vec2(x * m0 + y * m3 + m6, x * m1 + y * m4 + m7)

    def transform_direction(self, vector: UVec, normalize=False) -> Vec2:
        """Returns a transformed direction vector without translation."""
        m = self._matrix
        x, y = Vec2(vector)
        v = Vec2(x * m[0] + y * m[3], x * m[1] + y * m[4])
        return v.normalize() if normalize else v

    @classmethod
    def scale(cls, sx: float, sy: Optional[float] = None) -> Matrix33:
        """Returns a scaling transformation matrix. If `sy` is ``None``,`sy` = `sx`."""
        if sy is None:
            sy = sx
        m = cls()
        m._matrix = (float(sx), 0.0, 0.0, 0.0, float(sy), 0.0, 0.0, 0.0, 1.0)
        return m

    @classmethod
    def rotate(cls, angle: float) -> Matrix33:
        """Returns a rotation matrix about the z-axis.

        Args:
            angle: rotation angle in radians

        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        m = cls()
        m._matrix = (cos_a, sin_a, 0.0, -sin_a, cos_a, 0.0, 0.0, 0.0, 1.0)
        return m

    @classmethod
    def shear(cls, angle_x: float = 0, angle_y: float = 0) -> Matrix33:
        """Returns a translation matrix for shear mapping (visually similar
        to slanting) in the xy-plane.

        Args:
            angle_x: slanting angle in x direction in radians
            angle_y: slanting angle in y direction in radians

        """
        tx = math.tan(angle_x)
        ty = math.tan(angle_y)
        m = cls()
        m._matrix = (1.0, ty, 0.0, tx, 1.0, 0.0, 0.0, 0.0, 1.0)
        return m

    @staticmethod
    def chain(*matrices: Matrix33) -> Matrix33:
        """Compose a transformation matrix from one or more `matrices`."""
        try:
            transformation = matrices[0]
        except IndexError:
            return Matrix33()
        for matrix in matrices[1:]:
            transformation @= matrix
        return transformation

    def __matmul__(self, other: Matrix33) -> Matrix33:
        """Matrix multiplication."""
        m1 = self._matrix
        m2 = other._matrix
        m = self.__class__()
        # fmt: off
        m._matrix = (
            m1[0] * m2[0] + m1[1] * m2[3] + m1[2] * m2[6],
            m1[0] * m2[1] + m1[1] * m2[4] + m1[2] * m2[7],
            m1[0] * m2[2] + m1[1] * m2[5] + m1[2] * m2[8],

            m1[3] * m2[0] + m1[4] * m2[3] + m1[5] * m2[6],
            m1[3] * m2[1] + m1[4] * m2[4] + m1[5] * m2[7],
            m1[3] * m2[2] + m1[4] * m2[5] + m1[5] * m2[8],

            m1[6] * m2[0] + m1[7] * m2[3] + m1[8] * m2[6],
            m1[6] * m2[1] + m1[7] * m2[4] + m1[8] * m2[7],
            m1[6] * m2[2] + m1[7] * m2[5] + m1[8] * m2[8],
        )
        # fmt: on
        return m
