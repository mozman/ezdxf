# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, cast, Union
import math
from ezdxf.lldxf.const import DXFStructureError, DXFTypeError, VERTEXNAMES
from ezdxf.query import EntityQuery
from ezdxf.math import Vector, rytz_axis_construction, normalize_angle, bulge_to_arc, OCS
from ezdxf.entities import Line, Arc, Face3d

if TYPE_CHECKING:
    from ezdxf.eztypes import Insert, BaseLayout, DXFGraphic, Ellipse, LWPolyline, Polyline, Polyface, Polymesh


def explode_block_reference(block_ref: 'Insert', target_layout: 'BaseLayout') -> EntityQuery:
    """
    Explode a block reference into single DXF entities.

    Transforms the block entities into the required WCS location by applying the block reference
    attributes `insert`, `extrusion`, `rotation` and the scaling values `xscale`, `yscale` and `zscale`.
    Multiple inserts by row and column attributes is not supported.

    Returns an EntityQuery() container with all exploded DXF entities.

    Args:
        block_ref: Block reference entity (INSERT)
        target_layout: explicit target layout for exploded DXF entities

    .. warning::

        **Non uniform scaling** lead to incorrect results for text entities (TEXT, MTEXT, ATTRIB) and
        some other entities like ELLIPSE, SHAPE, HATCH with arc or ellipse path segments and
        POLYLINE/LWPOLYLINE with arc segments.

    (internal API)

    """
    if target_layout is None:
        raise DXFStructureError('Target layout is None.')

    if block_ref.doc is None:
        raise DXFStructureError('Block reference has to be assigned to a DXF document.')

    entitydb = block_ref.doc.entitydb
    if entitydb is None:
        raise DXFStructureError('Exploding a block reference requires an entity database.')

    entities = []

    for entity in virtual_block_reference_entities(block_ref):
        entitydb.add(entity)
        target_layout.add_entity(entity)
        entities.append(entity)

    # Process attached ATTRIB entities:
    for attrib in block_ref.attribs:
        # Attached ATTRIB entities are already located in the WCS
        target_layout.add_entity(attrib)
        entities.append(attrib)

    # Unlink attributes else they would be destroyed by deleting the block reference.
    block_ref.attribs = []
    source_layout = block_ref.get_layout()
    if source_layout is not None:
        # Remove and destroy exploded INSERT if assigned to a layout
        source_layout.delete_entity(block_ref)
    else:
        entitydb.delete_entity(block_ref)
    return EntityQuery(entities)


def virtual_block_reference_entities(block_ref: 'Insert') -> Iterable['DXFGraphic']:
    """
    Yields 'virtual' parts of block reference `block_ref`. This method is meant to examine the the block reference
    entities without the need to explode the block reference.

    This entities are located at the 'exploded' positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    Args:
        block_ref: Block reference entity (INSERT)

    .. warning::

        **Non uniform scaling** returns incorrect results for text entities (TEXT, MTEXT, ATTRIB) and
        some other entities like ELLIPSE, SHAPE, HATCH with arc or ellipse path segments and
        POLYLINE/LWPOLYLINE with arc segments.

    (internal API)

    """
    assert block_ref.dxftype() == 'INSERT'

    brcs = block_ref.brcs()
    # Non uniform scaling will produce incorrect results for some entities!
    xscale = block_ref.dxf.xscale
    yscale = block_ref.dxf.yscale
    uniform_scaling = max(abs(xscale), abs(yscale))
    non_uniform_scaling = xscale != yscale

    block_layout = block_ref.block()
    if block_layout is None:
        raise DXFStructureError(f'Required block definition for "{block_ref.dxf.name}" does not exist.')

    for entity in block_layout:
        dxftype = entity.dxftype()
        if dxftype == 'ATTDEF':  # do not explode ATTDEF entities
            continue

        # Copy entity with all DXF attributes
        try:
            copy = entity.copy()
        except DXFTypeError:
            continue  # non copyable entities will be ignored

        if non_uniform_scaling and dxftype in {'ARC', 'CIRCLE'}:
            from ezdxf.entities import Ellipse
            copy = Ellipse.from_arc(entity)
            dxftype = copy.dxftype()

        # Basic transformation from BRCS to WCS
        try:
            copy.transform_to_wcs(brcs)
        except NotImplementedError:  # entities without 'transform_to_ucs' support will be ignored
            continue

        # Apply DXF attribute scaling:
        # 1. simple entities without properties to scale
        if dxftype in {'LINE', 'POINT', 'LWPOLYLINE', 'POLYLINE', 'MESH', 'HATCH', 'SPLINE',
                       'SOLID', '3DFACE', 'TRACE', 'IMAGE', 'WIPEOUT', 'XLINE', 'RAY', 'LIGHT', 'HELIX'}:
            pass  # nothing else to do
        elif dxftype in {'CIRCLE', 'ARC'}:
            # simple uniform scaling of radius
            # Non uniform scaling: ARC, CIRCLE -> ELLIPSE
            copy.dxf.radius = entity.dxf.radius * uniform_scaling
        elif dxftype == 'ELLIPSE':
            if non_uniform_scaling:
                if entity.dxftype() == 'ELLIPSE':  # original entity is an ELLIPSE
                    ellipse = cast('Ellipse', entity)

                    # transform axis
                    conjugated_major_axis = brcs.direction_to_wcs(ellipse.dxf.major_axis)
                    conjugated_minor_axis = brcs.direction_to_wcs(ellipse.minor_axis)
                    major_axis, _, ratio = rytz_axis_construction(conjugated_major_axis, conjugated_minor_axis)
                    copy.dxf.major_axis = major_axis
                    copy.dxf.ratio = max(ratio, 1e-6)

                    # adjusting start- and end parameter
                    center = copy.dxf.center  # transformed center point
                    start_point, end_point = ellipse.vertices((ellipse.dxf.start_param, ellipse.dxd.end_param))
                    start_vec = brcs.to_wcs(start_point) - center
                    end_vec = brcs.to_wcs(end_point) - center
                    # The dot product (scalar product) is the angle between two vectors.
                    # https://en.wikipedia.org/wiki/Dot_product
                    # Not sure if this is the correct way to adjust start- and end parameter
                    copy.dxf.start_param = normalize_angle(major_axis.dot(start_vec))
                    copy.dxf.end_param = normalize_angle(major_axis.dot(end_vec))

                    if copy.dxf.ratio > 1:
                        copy.swap_axis()
                else:  # converted from ARC to ELLIPSE
                    ellipse = cast('Ellipse', copy)
                    ellipse.dxf.ratio = max(yscale / xscale, 1e-6)
                    if ellipse.dxf.ratio > 1:
                        ellipse.swap_axis()
        elif dxftype == 'MTEXT':
            # Scale MTEXT height/width just by uniform_scaling, how to handle non uniform scaling?
            copy.dxf.char_height *= uniform_scaling
            copy.dxf.width *= uniform_scaling
        elif dxftype in {'TEXT', 'ATTRIB'}:
            # Scale TEXT height just by uniform_scaling, how to handle non uniform scaling?
            copy.dxf.height *= uniform_scaling
        elif dxftype == 'INSERT':
            # Set scaling of child INSERT to scaling of parent INSERT
            for scale in ('xscale', 'yscale', 'zscale'):
                if block_ref.dxf.hasattr(scale):
                    original_scale = copy.dxf.get_default(scale)
                    block_ref_scale = block_ref.dxf.get(scale)
                    copy.dxf.set(scale, original_scale * block_ref_scale)
            if uniform_scaling != 1:
                # Scale attached ATTRIB entities:
                # Scale height just by uniform_scaling, how to handle non uniform scaling?
                for attrib in copy.attribs:
                    attrib.dxf.height *= uniform_scaling
        elif dxftype == 'SHAPE':
            # Scale SHAPE size just by uniform_scaling, how to handle non uniform scaling?
            copy.dxf.size *= uniform_scaling
        else:  # unsupported entity will be ignored
            continue
        yield copy


def explode_entity(entity: 'DXFGraphic', target_layout: 'BaseLayout' = None) -> 'EntityQuery':
    """
    Explode parts of an entity as primitives into target layout, if target layout is ``None``,
    the target layout is the layout of the POLYLINE.

    Returns an :class:`~ezdxf.query.EntityQuery` container with all DXF parts.

    Args:
        entity: DXF entity to explode, has to have a :meth:`virtual_entities()` method
        target_layout: target layout for DXF parts, ``None`` for same layout as source entity

    .. versionadded:: 0.12

    (internal API)

    """
    dxftype = entity.dxftype()
    if entity.doc is None:
        raise DXFStructureError(f'{dxftype} has to be assigned to a DXF document.')

    entitydb = entity.doc.entitydb
    if entitydb is None:
        raise DXFStructureError(f'{dxftype} requires an entity database.')

    if target_layout is None:
        target_layout = entity.get_layout()
        if target_layout is None:
            raise DXFStructureError(f'{dxftype} without layout assigment, specify target layout.')

    entities = []

    assert hasattr(entity, 'virtual_entities')
    for e in entity.virtual_entities():
        entitydb.add(e)
        target_layout.add_entity(e)
        entities.append(e)

    source_layout = entity.get_layout()
    if source_layout is not None:
        source_layout.delete_entity(entity)
    else:
        entitydb.delete_entity(entity)
    return EntityQuery(entities)


def virtual_lwpolyline_entities(lwpolyline: 'LWPolyline') -> Iterable[Union['Line', 'Arc']]:
    """
    Yields 'virtual' entities of LWPOLYLINE as LINE or ARC objects.

    This entities are located at the original positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    (internal API)

    """
    assert lwpolyline.dxftype() == 'LWPOLYLINE'

    points = lwpolyline.get_points('xyb')
    if len(points) < 2:
        return

    if lwpolyline.closed:
        points.append(points[0])

    yield from _virtual_polyline_entities(
        points=points,
        elevation=lwpolyline.dxf.elevation,
        extrusion=lwpolyline.dxf.get('extrusion', None),
        dxfattribs=lwpolyline.graphic_properties(),
        doc=lwpolyline.doc,
    )


def virtual_polyline_entities(polyline: 'Polyline') -> Iterable[Union['Line', 'Arc', 'Face3d']]:
    """
    Yields 'virtual' entities of POLYLINE as LINE, ARC or 3DFACE objects.

    This entities are located at the original positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    (internal API)

    """
    assert polyline.dxftype() == 'POLYLINE'
    if polyline.is_2d_polyline:
        return virtual_polyline2d_entities(polyline)
    elif polyline.is_3d_polyline:
        return virtual_polyline3d_entities(polyline)
    elif polyline.is_polygon_mesh:
        return virtual_polymesh_entities(polyline)
    elif polyline.is_poly_face_mesh:
        return virtual_polyface_entities(polyline)
    return []


def virtual_polyline2d_entities(polyline: 'Polyline') -> Iterable[Union['Line', 'Arc']]:
    """
    Yields 'virtual' entities of 2D POLYLINE as LINE or ARC objects.

    This entities are located at the original positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    (internal API)

    """
    assert polyline.dxftype() == 'POLYLINE'
    assert polyline.is_2d_polyline
    if len(polyline.vertices) < 2:
        return

    points = [(v.dxf.location.x, v.dxf.location.y, v.dxf.bulge) for v in polyline.vertices]
    if polyline.is_closed:
        points.append(points[0])

    yield from _virtual_polyline_entities(
        points=points,
        elevation=Vector(polyline.dxf.get('elevation', (0, 0, 0))).z,
        extrusion=polyline.dxf.get('extrusion', None),
        dxfattribs=polyline.graphic_properties(),
        doc=polyline.doc,
    )


def _virtual_polyline_entities(points, elevation: float, extrusion: Vector, dxfattribs: dict, doc) -> Iterable[
    Union['Line', 'Arc']]:
    ocs = OCS(extrusion) if extrusion else OCS()
    prev_point = None
    prev_bulge = None

    for x, y, bulge in points:
        point = Vector(x, y, elevation)
        if prev_point is None:
            prev_point = point
            prev_bulge = bulge
            continue

        attribs = dict(dxfattribs)
        if prev_bulge != 0:
            center, start_angle, end_angle, radius = bulge_to_arc(prev_point, point, prev_bulge)
            attribs['center'] = Vector(center.x, center.y, elevation)
            attribs['radius'] = radius
            attribs['start_angle'] = math.degrees(start_angle)
            attribs['end_angle'] = math.degrees(end_angle)
            if extrusion:
                attribs['extrusion'] = extrusion
            yield Arc.new(doc=doc, dxfattribs=attribs)
        else:
            attribs['start'] = ocs.to_wcs(prev_point)
            attribs['end'] = ocs.to_wcs(point)
            yield Line.new(doc=doc, dxfattribs=attribs)
        prev_point = point
        prev_bulge = bulge


def virtual_polyline3d_entities(polyline: 'Polyline') -> Iterable['Line']:
    """
    Yields 'virtual' entities of 3D POLYLINE as LINE objects.

    This entities are located at the original positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    (internal API)

    """
    assert polyline.dxftype() == 'POLYLINE'
    assert polyline.is_3d_polyline
    if len(polyline.vertices) < 2:
        return
    doc = polyline.doc
    vertices = polyline.vertices
    dxfattribs = polyline.graphic_properties()
    start = -1 if polyline.is_closed else 0
    for index in range(start, len(vertices) - 1):
        dxfattribs['start'] = vertices[index].dxf.location
        dxfattribs['end'] = vertices[index + 1].dxf.location
        yield Line.new(doc=doc, dxfattribs=dxfattribs)


def virtual_polymesh_entities(polyline: 'Polyline') -> Iterable['Face3d']:
    """
    Yields 'virtual' entities of POLYMESH as 3DFACE objects.

    This entities are located at the original positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    (internal API)

    """
    polymesh = cast('Polymesh', polyline)
    assert polymesh.dxftype() == 'POLYLINE'
    assert polymesh.is_polygon_mesh

    doc = polymesh.doc
    mesh = polymesh.get_mesh_vertex_cache()
    dxfattribs = polymesh.graphic_properties()
    m_count = polymesh.dxf.m_count
    n_count = polymesh.dxf.n_count
    m_range = m_count - int(not polymesh.is_m_closed)
    n_range = n_count - int(not polymesh.is_n_closed)

    for m in range(m_range):
        for n in range(n_range):
            next_m = (m + 1) % m_count
            next_n = (n + 1) % n_count

            dxfattribs['vtx0'] = mesh[m, n]
            dxfattribs['vtx1'] = mesh[next_m, n]
            dxfattribs['vtx2'] = mesh[next_m, next_n]
            dxfattribs['vtx3'] = mesh[m, next_n]
            yield Face3d.new(doc=doc, dxfattribs=dxfattribs)


def virtual_polyface_entities(polyline: 'Polyline') -> Iterable['Face3d']:
    """
    Yields 'virtual' entities of POLYFACE as 3DFACE objects.

    This entities are located at the original positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    (internal API)

    """
    assert polyline.dxftype() == 'POLYLINE'
    assert polyline.is_poly_face_mesh

    doc = polyline.doc
    vertices = polyline.vertices
    base_attribs = polyline.graphic_properties()

    face_records = (v for v in vertices if v.is_face_record)
    for face in face_records:
        face3d_attribs = dict(base_attribs)
        face3d_attribs.update(face.graphic_properties())
        invisible = 0
        pos = 1

        indices = ((face.dxf.get(name), name) for name in VERTEXNAMES if face.dxf.hasattr(name))
        for index, name in indices:
            # vertex indices are 1-based, negative indices indicate invisible edges
            if index < 0:
                index = abs(index)
                invisible += pos
            # python list `vertices` is 0-based
            face3d_attribs[name] = vertices[index - 1].dxf.location
            # vertex index bit encoded: 1=0b0001, 2=0b0010, 3=0b0100, 4=0b1000
            pos <<= 1

        face3d_attribs['invisible'] = invisible
        yield Face3d.new(doc=doc, dxfattribs=face3d_attribs)
