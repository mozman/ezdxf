# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence
import dataclasses

from ezdxf.lldxf import const
from ezdxf.entities import SpatialFilter, DXFEntity, Dictionary, Insert
from ezdxf.math import Vec2, Vec3, UVec, Z_AXIS, Matrix44, BoundingBox2d

__all__ = ["get_spatial_filter", "XClip", "ClippingPath"]

ACAD_FILTER = "ACAD_FILTER"
SPATIAL = "SPATIAL"


@dataclasses.dataclass
class ClippingPath:
    vertices: Sequence[Vec2]
    outer_boundary: Sequence[Vec2]
    is_inverted_path: bool = False


class XClip:
    """Helper class to manage the clipping path of INSERT entities.

    Provides a similar functionality as the XCLIP command in CAD applications.

    .. important::

        This class handles only 2D clipping paths.

    The visibility of the clipping path can be set individually for each block 
    reference, but the HEADER variable `$XCLIPFRAME` ultimately determines whether the 
    clipping path is displayed or plotted:
    
    === =============== ===
    0   not displayed   not plotted
    1   displayed       not plotted
    2   displayed       plotted
    === =============== ===

    The default setting is 2.

    """

    def __init__(self, insert: Insert) -> None:
        if not isinstance(insert, Insert):
            raise const.DXFTypeError(f"INSERT entity required, got {str(insert)}")
        self._insert = insert
        self._spatial_filter = get_spatial_filter(insert)

    def get_spatial_filter(self) -> SpatialFilter | None:
        """Returns the underlaying SPATIAL_FILTER entity if the INSERT entity has a
        clipping path and returns ``None`` otherwise.
        """
        return self._spatial_filter

    @property
    def has_clipping_path(self) -> bool:
        """Returns if the INSERT entity has a clipping path."""
        return self._spatial_filter is not None

    @property
    def is_clipping_path_visible(self) -> bool:
        """Returns if the clipping path polygon should be visible in CAD applications."""
        if isinstance(self._spatial_filter, SpatialFilter):
            return bool(self._spatial_filter.dxf.display_clipping_path)
        return False

    def show_clipping_path(self) -> None:
        """Display the clipping path polygon in CAD applications."""
        if isinstance(self._spatial_filter, SpatialFilter):
            self._spatial_filter.dxf.display_clipping_path = 1

    def hide_clipping_path(self) -> None:
        """Hide the clipping path polygon in CAD applications."""
        if isinstance(self._spatial_filter, SpatialFilter):
            self._spatial_filter.dxf.display_clipping_path = 0

    def get_block_clipping_path(self) -> ClippingPath:
        """Returns the clipping path in block coordinates (relative to the block origin)."""
        vertices: Sequence[Vec2] = []
        if not isinstance(self._spatial_filter, SpatialFilter):
            return ClippingPath(vertices, vertices)
        m = self._spatial_filter.inverse_insert_matrix
        vertices = Vec2.tuple(
            m.transform_vertices(self._spatial_filter.boundary_vertices)
        )
        if len(vertices) == 2:
            vertices = _rect_path(vertices)
        return ClippingPath(vertices, [], is_inverted_path=False)

    def get_wcs_clipping_path(self) -> ClippingPath:
        """Returns the clipping path in WCS coordinates (relative to the WCS origin) as
        2D path projected onto the xy-plane.
        """
        vertices: Sequence[Vec2] = tuple()
        if not isinstance(self._spatial_filter, SpatialFilter):
            return ClippingPath(vertices, vertices)
        block_clipping_path = self.get_block_clipping_path()
        m = self._insert.matrix44()
        vertices = Vec2.tuple(m.transform_vertices(block_clipping_path.vertices))
        outer_boundary_path = Vec2.tuple(
            m.transform_vertices(block_clipping_path.outer_boundary)
        )
        return ClippingPath(
            vertices, outer_boundary_path, block_clipping_path.is_inverted_path
        )

    def set_block_clipping_path(self, vertices: Iterable[UVec]) -> None:
        """Set clipping path in block coordinates (relative to block origin).

        The clipping path is located in the xy-plane, the z-axis of all vertices will
        be ignored.  The clipping path doesn't have to be closed (first vertex != last vertex).
        Two vertices define a rectangle where the sides are parallel to x- and y-axis.

        Raises:
           DXFValueError: clipping path has less than two vertrices

        """
        if self._spatial_filter is None:
            self._spatial_filter = new_spatial_filter(self._insert)
        spatial_filter = self._spatial_filter
        spatial_filter.set_boundary_vertices(vertices)
        spatial_filter.dxf.origin = Vec3(0, 0, 0)
        spatial_filter.dxf.extrusion = Z_AXIS
        spatial_filter.dxf.has_front_clipping_plane = 0
        spatial_filter.dxf.front_clipping_plane_distance = 0.0
        spatial_filter.dxf.has_back_clipping_plane = 0
        spatial_filter.dxf.back_clipping_plane_distance = 0.0

        # The clipping path set by ezdxf is always relative to the block origin and
        # therefore both transformation matrices are the identity matrix - which does
        # nothing.
        m = Matrix44()
        spatial_filter.set_inverse_insert_matrix(m)
        spatial_filter.set_transform_matrix(m)
        discard_inverted_clipping_path(spatial_filter)

    def set_wcs_clipping_path(self, vertices: Iterable[UVec]) -> None:
        """Set clipping path in WCS coordinates (relative to WCS origin).

        The clipping path is located in the xy-plane, the z-axis of all vertices will
        be ignored. The clipping path doesn't have to be closed (first vertex != last vertex).
        Two vertices define a rectangle where the sides are parallel to x- and y-axis.

        Raises:
           DXFValueError: clipping path has less than two vertrices
           ZeroDivisionError: Block reference transformation matrix is not invertible

        """
        m = self._insert.matrix44()
        try:
            m.inverse()
        except ZeroDivisionError:
            raise ZeroDivisionError(
                "Block reference transformation matrix is not invertible."
            )
        _vertices = Vec2.list(vertices)
        if len(_vertices) == 2:
            _vertices = _rect_path(_vertices)
        self.set_block_clipping_path(m.transform_vertices(_vertices))

    def discard_clipping_path(self) -> None:
        """Delete the clipping path. The clipping path doesn't have to exist.

        This method does not discard the extension dictionary of the base entity,
        even when its empty.
        """
        if not isinstance(self._spatial_filter, SpatialFilter):
            return

        xdict = self._insert.get_extension_dict()
        xdict.discard(ACAD_FILTER)
        entitydb = self._insert.doc.entitydb  # type: ignore
        assert entitydb is not None
        entitydb.delete_entity(self._spatial_filter)
        self._spatial_filter = None

    def cleanup(self):
        """Discard the extension dictionary of the base entity when empty."""
        self._insert.discard_empty_extension_dict()


def _rect_path(vertices: Iterable[Vec2]) -> Sequence[Vec2]:
    """Returns the path vertices for the smallest rectangular boundary around the given
    vertices.
    """
    return BoundingBox2d(vertices).rect_vertices()


def _outer_boundary_path(vertices: Iterable[Vec2], start: Vec2) -> Sequence[Vec2]:
    bbox = BoundingBox2d(vertices)
    assert (bbox.extmax is not None) and (bbox.extmin is not None)
    if not bbox.inside(start):
        raise ValueError("starting point is not inside the outer boundary")
    min_x, min_y = bbox.extmin
    max_x, max_y = bbox.extmax
    return (
        start,
        Vec2(start.x, max_y),
        Vec2(min_x, max_y),
        bbox.extmin,
        Vec2(max_x, min_y),
        bbox.extmax,
        Vec2(start.x, max_y),
        start,
    )


def _find_top_starting_point(vertices: Iterable[Vec2]) -> Vec2:
    return max(vertices, key=lambda v: v.y)


def get_spatial_filter(entity: DXFEntity) -> SpatialFilter | None:
    """Returns the underlaying SPATIAL_FILTER entity if the given `entity` has a
    clipping path and returns ``None`` otherwise.
    """
    try:
        xdict = entity.get_extension_dict()
    except AttributeError:
        return None
    acad_filter = xdict.get(ACAD_FILTER)
    if not isinstance(acad_filter, Dictionary):
        return None
    acad_spatial_filter = acad_filter.get(SPATIAL)
    if isinstance(acad_spatial_filter, SpatialFilter):
        return acad_spatial_filter
    return None


def new_spatial_filter(entity: DXFEntity) -> SpatialFilter:
    """Creates the extension dict, the sub-dictionary ACAD_FILTER and the SPATIAL_FILTER
    entity if not exist.
    """
    doc = entity.doc
    if doc is None:
        raise const.DXFTypeError("Cannot add new clipping path to virtual entity.")
    try:
        xdict = entity.get_extension_dict()
    except AttributeError:
        xdict = entity.new_extension_dict()
    acad_filter_dict = xdict.dictionary.get_required_dict(ACAD_FILTER)
    spatial_filter = acad_filter_dict.get(SPATIAL)
    if not isinstance(spatial_filter, SpatialFilter):
        spatial_filter = doc.objects.add_dxf_object_with_reactor(
            "SPATIAL_FILTER", {"owner": acad_filter_dict.dxf.handle}
        )
        acad_filter_dict.add(SPATIAL, spatial_filter)
    assert isinstance(spatial_filter, SpatialFilter)
    return spatial_filter


def discard_inverted_clipping_path(spatial_filter: SpatialFilter) -> None:
    # The inverted clipping path is stored in the extension dict by the key
    # ACAD_XREC_ROUNDTRIP.
    spatial_filter.discard_extension_dict()
