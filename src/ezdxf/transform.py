#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Iterator, NamedTuple
import enum

from ezdxf.math import (
    Matrix44,
    UVec,
    Vec3,
    NonUniformScalingError,
    InsertTransformationError,
)
from ezdxf.entities import DXFEntity, Circle, LWPolyline, Polyline

MIN_SCALING_FACTOR = 1e-12


class Error(enum.Enum):
    TRANSFORMATION_NOT_SUPPORTED = enum.auto()
    NON_UNIFORM_SCALING_ERROR = enum.auto()
    INSERT_TRANSFORMATION_ERROR = enum.auto()
    VIRTUAL_ENTITY_NOT_SUPPORTED = enum.auto()


class Logger:
    class Entry(NamedTuple):
        error: Error
        message: str
        entity: DXFEntity

    def __init__(self) -> None:
        self._entries: list[Logger.Entry] = []

    def __getitem__(self, index: int) -> Entry:
        """Returns the error entry at `index`."""
        return self._entries[index]

    def __iter__(self) -> Iterator[Entry]:
        """Iterates over all error entries."""
        return iter(self._entries)

    def __len__(self) -> int:
        """Returns the count of error entries."""
        return len(self._entries)

    def add(self, error: Error, message: str, entity: DXFEntity):
        self._entries.append(Logger.Entry(error, message, entity))

    def messages(self) -> list[str]:
        """Returns all error messages as list of strings."""
        return [entry.message for entry in self._entries]

    def purge(self, entries: Iterable[Entry]) -> None:
        for entry in entries:
            try:
                self._entries.remove(entry)
            except ValueError:
                pass


def matrix(entities: Iterable[DXFEntity], m: Matrix44) -> Logger:
    """Transforms the given `entities` inplace by the transformation matrix `m`,
    non-uniform scaling is not supported. The function logs errors and does not raise
    errors for unsupported entities or transformations that cannot be performed,
    see enum :class:`Error`.
    The :func:`matrix` function supports virtual entities as well.

    """
    log = Logger()
    for entity in entities:
        try:
            entity.transform(m)  # type: ignore
        except (AttributeError, NotImplementedError):
            msg = f"{str(entity)} entity does not support transformation"
            log.add(Error.TRANSFORMATION_NOT_SUPPORTED, msg, entity)
        except NonUniformScalingError:
            msg = f"{str(entity)} entity does not support non-uniform scaling"
            log.add(Error.NON_UNIFORM_SCALING_ERROR, msg, entity)
        except InsertTransformationError:
            msg = f"{str(entity)} entity can not represent a non-orthogonal target coordinate system"
            log.add(Error.INSERT_TRANSFORMATION_ERROR, msg, entity)

    return log


def matrix_ext(
    entities: Iterable[DXFEntity],
    m: Matrix44,
) -> Logger:
    """Transforms the given `entities` inplace by the transformation matrix `m`,
    non-uniform scaling is supported. The function converts circular arcs into ellipses
    to perform non-uniform scaling.  The function logs errors and does not raise errors
    for unsupported entities or transformation errors, see enum :class:`Error`.

    .. important::

        The :func:`matrix_ext` function does not support type conversion for virtual
        entities e.g. non-uniform scaling for CIRCLE, ARC or POLYLINE with bulges.

    """
    log = matrix(entities, m)
    errors: list[Logger.Entry] = []
    for entry in log:
        if entry.error != Error.NON_UNIFORM_SCALING_ERROR:
            continue

        errors.append(entry)
        entity = entry.entity
        if entity.is_virtual:
            msg = f"non-uniform scaling is not supported for virtual entity {str(entity)}"
            log.add(Error.VIRTUAL_ENTITY_NOT_SUPPORTED, msg, entity)
            continue

        if isinstance(entity, Circle):  # CIRCLE, ARC
            ellipse = entity.to_ellipse(replace=True)
            ellipse.transform(m)
        elif isinstance(entity, (LWPolyline, Polyline)):  # has bulges (circular arcs)
            for sub_entity in entity.explode():
                if isinstance(sub_entity, Circle):
                    sub_entity = sub_entity.to_ellipse()
                sub_entity.transform(m)  # type: ignore
    log.purge(errors)
    return log


def translate(entities: Iterable[DXFEntity], offset: UVec) -> Logger:
    """Translates (moves) `entities` inplace by the `offset` vector."""
    v = Vec3(offset)
    if v:
        return matrix(entities, m=Matrix44.translate(v.x, v.y, v.z))
    return Logger()


def scale_uniform(entities: Iterable[DXFEntity], factor: float) -> Logger:
    """Scales `entities` inplace by a `factor` in all axis. Scaling factors smaller than
    :attr:`MIN_SCALING_FACTOR` are ignored.

    """
    f = float(factor)
    if abs(f) > MIN_SCALING_FACTOR:
        return matrix(entities, m=Matrix44.scale(f, f, f))
    return Logger()


def scale(entities: Iterable[DXFEntity], sx: float, sy: float, sz: float) -> Logger:
    """Scales `entities` inplace by the factors `sx` in x-axis, `sy` in y-axis and `sz`
    in z-axis. Scaling factors smaller than :attr:`MIN_SCALING_FACTOR` are ignored.

    .. important::

        same limitations for virtual entities as the :func:`matrix_ext` function

    """

    def safe(f: float) -> float:
        f = float(f)
        return f if abs(f) > MIN_SCALING_FACTOR else 1.0

    return matrix_ext(entities, Matrix44.scale(safe(sx), safe(sy), safe(sz)))


def x_rotate(entities: Iterable[DXFEntity], angle: float) -> Logger:
    """Rotates `entities` inplace by `angle` in radians about the x-axis."""
    a = float(angle)
    if a:
        return matrix(entities, m=Matrix44.x_rotate(a))
    return Logger()


def y_rotate(entities: Iterable[DXFEntity], angle: float) -> Logger:
    """Rotates `entities` inplace by `angle` in radians about the y-axis."""
    a = float(angle)
    if a:
        return matrix(entities, m=Matrix44.y_rotate(a))
    return Logger()


def z_rotate(entities: Iterable[DXFEntity], angle: float) -> Logger:
    """Rotates `entities` inplace by `angle` in radians about the x-axis."""
    a = float(angle)
    if a:
        return matrix(entities, m=Matrix44.z_rotate(a))
    return Logger()


def axis_rotate(entities: Iterable[DXFEntity], axis: UVec, angle: float) -> Logger:
    """Rotates `entities` inplace by `angle` in radians about the rotation axis starting
    at the origin pointing in `axis` direction.
    """
    a = float(angle)
    if not a:
        return Logger()

    v = Vec3(axis)
    if not v.is_null:
        return matrix(entities, m=Matrix44.axis_rotate(v, a))
    return Logger()
