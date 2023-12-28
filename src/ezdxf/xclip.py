# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence
import dataclasses

from ezdxf.lldxf import const
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import dxftag
from ezdxf.entities import SpatialFilter, DXFEntity, Dictionary, Insert, XRecord
from ezdxf.math import Vec2, Vec3, UVec, Z_AXIS, Matrix44, BoundingBox2d
from ezdxf.entities.acad_xrec_roundtrip import RoundtripXRecord

__all__ = ["get_spatial_filter", "XClip", "ClippingPath"]

ACAD_FILTER = "ACAD_FILTER"
ACAD_XREC_ROUNDTRIP = "ACAD_XREC_ROUNDTRIP"
ACAD_INVERTEDCLIP_ROUNDTRIP = "ACAD_INVERTEDCLIP_ROUNDTRIP"
ACAD_INVERTEDCLIP_ROUNDTRIP_COMPARE = "ACAD_INVERTEDCLIP_ROUNDTRIP_COMPARE"

SPATIAL = "SPATIAL"


@dataclasses.dataclass
class ClippingPath:
    vertices: Sequence[Vec2]
    outer_boundary: Sequence[Vec2]
    is_inverted_clip: bool = False


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

    @property
    def is_inverted_clip(self) -> bool:
        """Returns ``True`` if clipping path is inverted."""
        xrec = get_roundtrip_xrecord(self._spatial_filter)
        if xrec is None:
            return False
        return xrec.has_section(ACAD_INVERTEDCLIP_ROUNDTRIP)

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

        is_inverted_clip = False
        outer_boundary: Sequence[Vec2] = tuple()
        xrec = get_roundtrip_xrecord(self._spatial_filter)
        if isinstance(xrec, RoundtripXRecord):
            inner_path_vertices = get_inner_path_vertices(xrec, m)
            if inner_path_vertices:
                outer_boundary = vertices
                vertices = inner_path_vertices
                is_inverted_clip = True

        return ClippingPath(vertices, outer_boundary, is_inverted_clip)

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
            vertices, outer_boundary_path, block_clipping_path.is_inverted_clip
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
        self._discard_inverted_clip()

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

    def invert_clipping_path(self, extents: Iterable[UVec] | None = None) -> None:
        """Invert cliping path. The outer boundary is defined by the bounding box of the
        given `extents` vertices or auto-detected if `extents` is ``None``.

        The `extents` are BLOCK coordinates.
        Requires an existing clipping path and that clipping path cannot be inverted.

        .. warning::

            AutoCAD will not load DXF files with inverted clipping paths created by
            ezdxf!!!!

        """
        current_clipping_path = self.get_block_clipping_path()
        if len(current_clipping_path.vertices) < 2:
            raise const.DXFValueError("no clipping path set")
        if current_clipping_path.is_inverted_clip:
            raise const.DXFValueError("clipping path is already inverted")
        
        assert self._insert.doc is not None
        self._insert.doc.add_acad_incompatibility_message(
            "AutoCAD will not load DXF files with inverted clipping paths created by ezdxf!!!!"
        )
        grow_factor = 0.0
        if extents is None:
            extents = self._detect_block_extents()
            # grow bounding box by 10%, bbox detection is not very precise for text
            # based entities:
            grow_factor = 0.1

        bbox = BoundingBox2d(extents)
        if bbox.extmin is None or bbox.extmax is None:
            raise const.DXFValueError("extents not detectable")

        if grow_factor:
            bbox.grow(max(bbox.size) * grow_factor)

        inner_path_vertices = current_clipping_path.vertices
        full_path_vertices = _inverted_boundary_path(bbox, inner_path_vertices)
        self.set_block_clipping_path(full_path_vertices)
        self._set_inverted_clipping_path(inner_path_vertices, full_path_vertices)

    def _detect_block_extents(self) -> Sequence[Vec2]:
        from ezdxf import bbox

        insert = self._insert
        doc = insert.doc
        assert doc is not None, "valid DXF document required"
        no_vertices: Sequence[Vec2] = tuple()
        block = doc.blocks.get(insert.dxf.name)
        if block is None:
            return no_vertices

        _bbox = bbox.extents(block, fast=True)
        if _bbox.extmin is None or _bbox.extmax is None:
            return no_vertices
        return Vec2.tuple([_bbox.extmin, _bbox.extmax])

    def _set_inverted_clipping_path(
        self, clip_vertices: Iterable[Vec2], compare_vertices: Iterable[Vec2]
    ) -> None:
        spatial_filter = self._spatial_filter
        assert isinstance(spatial_filter, SpatialFilter)
        xrec = get_roundtrip_xrecord(spatial_filter)
        if xrec is None:
            xrec = new_roundtrip_xrecord(spatial_filter)

        clip_tags = Tags(dxftag(10, Vec3(v)) for v in clip_vertices)
        compare_tags = Tags(dxftag(10, Vec3(v)) for v in compare_vertices)
        xrec.set_section(ACAD_INVERTEDCLIP_ROUNDTRIP, clip_tags)
        xrec.set_section(ACAD_INVERTEDCLIP_ROUNDTRIP_COMPARE, compare_tags)

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

    def _discard_inverted_clip(self) -> None:
        if isinstance(self._spatial_filter, SpatialFilter):
            self._spatial_filter.discard_extension_dict()

    def cleanup(self):
        """Discard the extension dictionary of the base entity when empty."""
        self._insert.discard_empty_extension_dict()


def _rect_path(vertices: Iterable[Vec2]) -> Sequence[Vec2]:
    """Returns the path vertices for the smallest rectangular boundary around the given
    vertices.
    """
    return BoundingBox2d(vertices).rect_vertices()


def _inverted_boundary_path(
    bbox: BoundingBox2d, hole: Sequence[Vec2]
) -> Sequence[Vec2]:
    assert (bbox.extmax is not None) and (bbox.extmin is not None)

    inverted_path = list(hole)
    start = hole[-1]

    min_x, min_y = bbox.extmin
    max_x, max_y = bbox.extmax
    dist_left = start.x - min_x
    dist_right = max_x - start.x
    dist_top = max_y - start.y
    dist_bottom = start.y - min_y
    min_dist = min(dist_left, dist_right, dist_bottom, dist_top)
    if min_dist == dist_top:
        inverted_path.extend(
            (
                Vec2(start.x, max_y),
                Vec2(max_x, max_y),
                Vec2(max_x, min_y),
                Vec2(min_x, min_y),
                Vec2(min_x, max_y),
                Vec2(start.x, max_y),
                start,
            )
        )
    elif min_dist == dist_bottom:
        inverted_path.extend(
            (
                Vec2(start.x, min_y),
                Vec2(min_x, min_y),
                Vec2(min_x, max_y),
                Vec2(max_x, max_y),
                Vec2(max_x, min_y),
                Vec2(start.x, min_y),
                start,
            )
        )
    elif min_dist == dist_left:
        inverted_path.extend(
            (
                Vec2(min_x, start.y),
                Vec2(min_x, max_y),
                Vec2(max_x, max_y),
                Vec2(max_x, min_y),
                Vec2(min_x, min_y),
                Vec2(min_x, start.y),
                start,
            )
        )
    elif min_dist == dist_right:
        inverted_path.extend(
            (
                Vec2(max_x, start.y),
                Vec2(max_x, min_y),
                Vec2(min_x, min_y),
                Vec2(min_x, max_y),
                Vec2(max_x, max_y),
                Vec2(max_x, start.y),
                start,
            )
        )
    return inverted_path


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


def new_roundtrip_xrecord(spatial_filter: SpatialFilter) -> RoundtripXRecord:
    try:
        xdict = spatial_filter.get_extension_dict()
    except AttributeError:
        xdict = spatial_filter.new_extension_dict()
    xrec = xdict.get(ACAD_XREC_ROUNDTRIP)
    if xrec is None:
        xrec = xdict.add_xrecord(ACAD_XREC_ROUNDTRIP)
        xrec.set_reactors([xdict.handle])
    assert isinstance(xrec, XRecord)
    return RoundtripXRecord(xrec)


def get_roundtrip_xrecord(
    spatial_filter: SpatialFilter | None,
) -> RoundtripXRecord | None:
    if spatial_filter is None:
        return None
    try:
        xdict = spatial_filter.get_extension_dict()
    except AttributeError:
        return None
    xrecord = xdict.get(ACAD_XREC_ROUNDTRIP)
    if isinstance(xrecord, XRecord):
        return RoundtripXRecord(xrecord)
    return None


def get_inner_path_vertices(xrec: RoundtripXRecord, m: Matrix44) -> Sequence[Vec2]:
    tags = xrec.get_section(ACAD_INVERTEDCLIP_ROUNDTRIP)
    vertices = m.transform_vertices(Vec3(t.value) for t in tags)
    return Vec2.tuple(vertices)
