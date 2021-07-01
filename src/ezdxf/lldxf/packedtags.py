# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from array import array
from typing import Iterable, MutableSequence, Sequence

from .types import DXFTag
from .const import DXFTypeError, DXFIndexError, DXFValueError
from .tags import Tags
from ezdxf.tools.indexing import Index
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.math import Matrix44


class TagList:
    """Store data in a standard Python ``list``."""

    __slots__ = ("values",)

    def __init__(self, data: Iterable = None):
        self.values: MutableSequence = list(data or [])

    def clone(self) -> "TagList":
        """Returns a deep copy."""
        return self.__class__(data=self.values)

    @classmethod
    def from_tags(cls, tags: Tags, code: int) -> "TagList":
        """
        Setup list from iterable tags.

        Args:
            tags: tag collection as :class:`~ezdxf.lldxf.tags.Tags`
            code: group code to collect

        """
        return cls(data=(tag.value for tag in tags if tag.code == code))

    def clear(self) -> None:
        """Delete all data values."""
        del self.values[:]


class TagArray(TagList):
    """Store data in an :class:`array.array`. Array type is defined by class
    variable ``DTYPE``.
    """

    __slots__ = ("values",)
    # Defines the data type of array.array()
    DTYPE = "i"

    def __init__(self, data: Iterable = None):
        self.values: array = array(self.DTYPE, data or [])

    def set_values(self, values: Iterable) -> None:
        """Replace data by `values`."""
        self.values[:] = array(self.DTYPE, values)


class VertexArray:
    """Store vertices in an ``array.array('d')``. Vertex size is defined by
    class variable ``VERTEX_SIZE``.
    """

    # Defines the vertex size
    VERTEX_SIZE = 3  # set to 2 for 2d points
    __slots__ = ("values",)

    def __init__(self, data: Iterable = None):
        self.values = array("d", data or [])

    def __len__(self) -> int:
        """Count of vertices."""
        return len(self.values) // self.VERTEX_SIZE

    def __getitem__(self, index: int):
        """Get vertex at `index`, extended slicing supported."""
        if isinstance(index, slice):
            return list(self._get_points(self._slicing(index)))
        else:
            return self._get_point(self._index(index))

    def __setitem__(self, index: int, point: Sequence[float]) -> None:
        """Set vertex `point` at `index`, extended slicing not supported."""
        if isinstance(index, slice):
            raise DXFTypeError("slicing not supported")
        else:
            self._set_point(self._index(index), point)

    def __delitem__(self, index: int) -> None:
        """Delete vertex at `index`, extended slicing supported."""
        if isinstance(index, slice):
            self._del_points(self._slicing(index))
        else:
            self._del_point(self._index(index))

    def __str__(self) -> str:
        """String representation."""
        name = self.__class__.__name__
        data = ",\n".join(str(p) for p in self)  # type: ignore
        return "{} = [\n{}\n]".format(name, data)

    def __iter__(self) -> Iterable[Sequence[float]]:
        """Returns iterable of vertices."""
        size = self.VERTEX_SIZE
        values = self.values
        index = 0
        len_array = len(values)
        while index < len_array:
            yield tuple(values[index : index + size])
            index += size

    def insert(self, pos: int, point: Sequence[float]):
        """Insert `point` in front of vertex at index `pos`.

        Args:
            pos: insert position
            point: point as tuple

        """
        size = self.VERTEX_SIZE
        if len(point) != size:
            raise DXFValueError(
                "point requires exact {} components.".format(size)
            )

        pos = self._index(pos) * size
        _insert = self.values.insert
        for value in reversed(point):
            _insert(pos, value)

    def clone(self) -> "VertexArray":
        """Returns a deep copy."""
        return self.__class__(data=self.values)

    @classmethod
    def from_tags(cls, tags: Iterable[DXFTag], code: int = 10) -> "VertexArray":
        """Setup point array from iterable tags.

        Args:
            tags: iterable of :class:`~ezdxf.lldxf.types.DXFVertex`
            code: group code to collect

        """
        vertices = array("d")
        for tag in tags:
            if tag.code == code:
                vertices.extend(tag.value)  # type: ignore
        return cls(data=vertices)

    def _index(self, item) -> int:
        return Index(self).index(item, error=DXFIndexError)

    def _slicing(self, index) -> Iterable[int]:
        return Index(self).slicing(index)

    def _get_point(self, index: int) -> Sequence[float]:
        size = self.VERTEX_SIZE
        index = index * size
        return tuple(self.values[index : index + size])

    def _get_points(self, indices) -> Iterable:
        for index in indices:
            yield self._get_point(index)

    def _set_point(self, index: int, point: Sequence[float]):
        size = self.VERTEX_SIZE
        if len(point) != size:
            raise DXFValueError(f"point requires exact {size} components.")
        if isinstance(point, (tuple, list)):
            point = array("d", point)
        index = index * size
        self.values[index : index + size] = point  # type: ignore

    def _del_point(self, index: int) -> None:
        size = self.VERTEX_SIZE
        pos = index * size
        del self.values[pos : pos + size]

    def _del_points(self, indices: Iterable[int]) -> None:
        del_flags = set(indices)
        size = self.VERTEX_SIZE
        survivors = array(
            "d",
            (
                v
                for i, v in enumerate(self.values)
                if (i // size) not in del_flags
            ),
        )
        self.values = survivors

    def export_dxf(self, tagwriter: "TagWriter", code=10):
        delta = 0
        for c in self.values:
            tagwriter.write_tag2(code + delta, c)
            delta += 10
            if delta > 20:
                delta = 0

    def append(self, point: Sequence[float]) -> None:
        """Append `point`."""
        if len(point) != self.VERTEX_SIZE:
            raise DXFValueError(
                f"point requires exact {self.VERTEX_SIZE} components."
            )
        self.values.extend(point)

    def extend(self, points: Iterable[Sequence[float]]) -> None:
        """Extend array by `points`."""
        for point in points:
            self.append(point)

    def clear(self) -> None:
        """Delete all vertices."""
        del self.values[:]

    def set(self, points: Iterable[Sequence[float]]) -> None:
        """Replace all vertices by `points`."""
        self.clear()
        self.extend(points)

    def transform(self, m: Matrix44) -> None:
        """Transform vertices by transformation matrix `m`."""
        values = array("d")
        for vertex in m.transform_vertices(self):
            values.extend(vertex)
        self.values = values
