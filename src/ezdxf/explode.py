# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, cast, Union, Tuple, Generator
import math
import logging
from ezdxf.lldxf.const import DXFStructureError, DXFTypeError, VERTEXNAMES
from ezdxf.query import EntityQuery
from ezdxf.math import Vector, rytz_axis_construction, normalize_angle, bulge_to_arc, OCS, quadrant
from ezdxf.entities import factory

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import Insert, BaseLayout, DXFGraphic, LWPolyline, Polyline, Attrib, Line, Arc, Face3d, Text

_2PI = math.pi * 2


def explode_block_reference(block_ref: 'Insert', target_layout: 'BaseLayout',
                            uniform_scaling_factor: float = None) -> EntityQuery:
    """
    Explode a block reference into single DXF entities.

    Transforms the block entities into the required WCS location by applying the block reference
    attributes `insert`, `extrusion`, `rotation` and the scaling values `xscale`, `yscale` and `zscale`.
    Multiple inserts by row and column attributes is not supported.

    Returns an EntityQuery() container with all exploded DXF entities.

    Attached ATTRIB entities are converted to TEXT entities, this is the behavior of the BURST command of
    the AutoCAD Express Tools.

    Args:
        block_ref: Block reference entity (INSERT)
        target_layout: explicit target layout for exploded DXF entities
        uniform_scaling_factor: override uniform scaling factor for text entities (TEXT, ATTRIB, MTEXT)  and
                                HATCH pattern, default is ``max(abs(xscale), abs(yscale),  abs(zscale))``

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
    assert entitydb is not None, 'Exploding a block reference requires an entity database.'

    dxffactory = block_ref.doc.dxffactory
    assert dxffactory is not None, 'Exploding a block reference requires a DXF entity factory.'

    entities = []

    for entity in virtual_block_reference_entities(block_ref, uniform_scaling_factor=uniform_scaling_factor):
        dxftype = entity.dxftype()
        entitydb.add(entity)
        target_layout.add_entity(entity)
        if dxftype == 'DIMENSION':
            # Render a graphical representation for each exploded DIMENSION entity as anonymous block.
            cast('Dimension', entity).render()
        entities.append(entity)

    # Convert attached ATTRIB entities to TEXT entities:
    # This is the behavior of the BURST command of the AutoCAD Express Tools
    for attrib in block_ref.attribs:
        # Attached ATTRIB entities are already located in the WCS
        text = attrib_to_text(attrib, dxffactory)
        target_layout.add_entity(text)
        entities.append(text)

    source_layout = block_ref.get_layout()
    if source_layout is not None:
        # Remove and destroy exploded INSERT if assigned to a layout
        source_layout.delete_entity(block_ref)
    else:
        entitydb.delete_entity(block_ref)
    return EntityQuery(entities)


IGNORE_FROM_ATTRIB = {'version', 'prompt', 'tag', 'flags', 'field_length', 'lock_position'}


def attrib_to_text(attrib: 'Attrib', dxffactory) -> 'Text':
    dxfattribs = attrib.dxfattribs(drop=IGNORE_FROM_ATTRIB)
    # ATTRIB has same owner as INSERT but does not reside in any EntitySpace() and must not deleted from any layout.
    dxffactory.doc.entitydb.delete_entity(attrib)
    # New TEXT entity has same handle as the deleted ATTRIB entity and replaces the ATTRIB entity in the database.
    return dxffactory.create_db_entry('TEXT', dxfattribs=dxfattribs)


def angle_to_param(ratio: float, angle: float, quadrant: int = 0) -> float:
    """ Returns ellipse parameter for argument `angle`.

    Args:
        ratio: minor axis to major axis ratio as stored in the ELLIPSE entity (always < 1).
        angle: angle between major axis and line from center to point on the ellipse
        quadrant: quadrant of the angle, use to ``0`` for no adjustment.

    """
    # source: http://www.petercollingridge.co.uk/tutorials/computational-geometry/finding-angle-around-ellipse/
    result = math.atan(1.0 / ratio * math.tan(angle))

    if quadrant in (2, 3):
        result += math.pi
    if quadrant in (3, 4):
        result = -result
    return result


def virtual_block_reference_entities(block_ref: 'Insert',
                                     uniform_scaling_factor: float = None,
                                     only_return_skipped_entities: bool = False) -> Iterable['DXFGraphic']:
    """
    Yields 'virtual' parts of block reference `block_ref`. This method is meant to examine the the block reference
    entities without the need to explode the block reference.

    This entities are located at the 'exploded' positions, but are not stored in the entity database, have no handle
    and are not assigned to any layout.

    Args:
        block_ref: Block reference entity (INSERT)
        uniform_scaling_factor: override uniform scaling factor for text entities (TEXT, ATTRIB, MTEXT)  and
                                HATCH pattern, default is ``max(abs(xscale), abs(yscale),  abs(zscale))``
        only_return_skipped_entities: rather than returning the entities whose transformation is supported,
                                return any entities that were skipped for any reason.

    .. warning::

        **Non uniform scaling** returns incorrect results for text entities (TEXT, MTEXT, ATTRIB) and
        some other entities like ELLIPSE, SHAPE, HATCH with arc or ellipse path segments and
        POLYLINE/LWPOLYLINE with arc segments.

    (internal API)

    """
    assert block_ref.dxftype() == 'INSERT'
    Ellipse = cast('Ellipse', factory.cls('ELLIPSE'))

    def disassemble(layout) -> Generator[Tuple[bool, 'DXFGraphic'], None, None]:
        for entity in layout:
            dxftype = entity.dxftype()
            if dxftype == 'ATTDEF':  # do not explode ATTDEF entities
                yield True, entity
                continue

            if has_non_uniform_scaling:
                if dxftype in {'ARC', 'CIRCLE'}:
                    # convert ARC to ELLIPSE
                    yield False, Ellipse.from_arc(entity)
                    continue
                if dxftype in {'LWPOLYLINE', 'POLYLINE'} and entity.has_arc:
                    # disassemble (LW)POLYLINE into LINE and ARC segments
                    for segment in entity.virtual_entities():
                        # convert ARC to ELLIPSE
                        if segment.dxftype() == 'ARC':
                            yield False, Ellipse.from_arc(segment)
                        else:
                            yield False, segment
                    continue

            # Copy entity with all DXF attributes
            try:
                copy = entity.copy()
            except DXFTypeError:
                logger.debug(f'(Virtual Block Reference Entities) Ignoring non copyable entity {str(entity)}')
                yield True, entity
                continue  # non copyable entities will be ignored

            if copy.dxftype() == 'HATCH':
                if copy.dxf.associative:
                    # remove associations
                    copy.dxf.associative = 0
                    for path in copy.paths:
                        path.source_boundary_objects = []

                if has_non_uniform_scaling and copy.paths.has_critical_elements():
                    # None uniform scaling produces incorrect results for the arc and ellipse transformations.
                    # This causes an DXF structure error for AutoCAD.
                    # todo: requires testing
                    logger.debug(f'(Virtual Block Reference Entities) Ignoring {str(entity)} for non uniform scaling.')
                    yield True, entity
                    continue

                    # For the case that arc and ellipse transformation works correct someday:
                    # copy.paths.arc_edges_to_ellipse_edges()

            yield False, copy

    brcs = block_ref.brcs()
    block_layout = block_ref.block()
    if block_layout is None:
        raise DXFStructureError(f'Required block definition for "{block_ref.dxf.name}" does not exist.')

    has_scaling = block_ref.has_scaling
    if has_scaling:
        xscale = block_ref.dxf.xscale
        yscale = block_ref.dxf.yscale
        zscale = block_ref.dxf.zscale

        if uniform_scaling_factor is not None:
            uniform_scaling_factor = float(uniform_scaling_factor)
        else:
            uniform_scaling_factor = block_ref.text_scaling

        # Non uniform scaling will produce incorrect results for some entities!
        if xscale == yscale == zscale:
            has_non_uniform_scaling = False
            if xscale == 1:  # yscale == 1, zscale == 1
                has_scaling = False
        else:
            has_non_uniform_scaling = True
    else:
        xscale, yscale, zscale = (1, 1, 1)
        uniform_scaling_factor = 1
        has_non_uniform_scaling = False

    for entity_skipped, entity in disassemble(block_layout):
        if entity_skipped:
            if only_return_skipped_entities:
                yield entity
            continue

        dxftype = entity.dxftype()

        if has_non_uniform_scaling and dxftype == 'ELLIPSE':
            # transform start- and end location before main transformation
            ellipse = cast('Ellipse', entity)
            open_ellipse = not math.isclose(
                normalize_angle(ellipse.dxf.start_param),
                normalize_angle(ellipse.dxf.end_param),
            )
            if open_ellipse:
                # transformed start- and end point
                start_param = ellipse.dxf.start_param
                end_param = ellipse.dxf.end_param
                start_point, end_point = brcs.points_to_wcs(ellipse.vertices((start_param, end_param)))
            minor_axis = brcs.direction_to_wcs(ellipse.minor_axis)

        # Basic transformation from BRCS to WCS
        try:
            entity.transform_to_wcs(brcs)
        except NotImplementedError:  # entities without 'transform_to_wcs' support will be ignored
            logger.debug(f'(Virtual Block Reference Entities) Ignoring non transformable entity {str(entity)}')
            if only_return_skipped_entities:
                yield entity
            continue

        if has_scaling:
            # Apply DXF attribute scaling:
            # Simple entities without properties to scale
            if dxftype in {'LINE', 'POINT', 'LWPOLYLINE', 'POLYLINE', 'MESH', 'SPLINE', 'SOLID', '3DFACE', 'TRACE',
                           'IMAGE', 'WIPEOUT', 'XLINE', 'RAY', 'LIGHT', 'HELIX'}:
                pass  # nothing else to do
            elif dxftype in {'CIRCLE', 'ARC'}:
                # Non uniform scaling: ARC and CIRCLE converted to ELLIPSE
                entity.dxf.radius = entity.dxf.radius * uniform_scaling_factor
            elif dxftype == 'ELLIPSE' and not has_non_uniform_scaling:
                pass  # nothing else to do
            elif dxftype == 'ELLIPSE' and has_non_uniform_scaling:
                ellipse = cast('Ellipse', entity)
                # Transform axis
                major_axis = ellipse.dxf.major_axis
                if not math.isclose(major_axis.dot(minor_axis), 0):
                    major_axis, _, ratio = rytz_axis_construction(major_axis, minor_axis)
                else:
                    ratio = minor_axis.magnitude / major_axis.magnitude

                ellipse.dxf.major_axis = major_axis
                ellipse.dxf.ratio = max(ratio, 1e-6)
                if open_ellipse:
                    # adjusting start- and end parameter
                    center = ellipse.dxf.center  # transformed center point
                    start_angle = major_axis.angle_between(start_point - center)
                    end_angle = major_axis.angle_between(end_point - center)
                    # todo: quadrant detection may fail if the rytz's axis construction algorithm is applied
                    ellipse.dxf.start_param = angle_to_param(ratio, start_angle, quadrant(start_param))
                    ellipse.dxf.end_param = angle_to_param(ratio, end_angle, quadrant(end_param))

                if ellipse.dxf.ratio > 1:
                    ellipse.swap_axis()
            elif dxftype == 'MTEXT':
                # Scale MTEXT height/width just by uniform_scaling.
                entity.dxf.char_height *= uniform_scaling_factor
                entity.dxf.width *= uniform_scaling_factor
            elif dxftype in {'TEXT', 'ATTRIB'}:
                # Scale TEXT height just by uniform_scaling.
                entity.dxf.height *= uniform_scaling_factor
            elif dxftype == 'INSERT':
                # Set scaling of child INSERT to scaling of parent INSERT
                entity.dxf.xscale *= xscale
                entity.dxf.yscale *= yscale
                entity.dxf.zscale *= zscale
                # Scale attached ATTRIB entities:
                for attrib in entity.attribs:
                    attrib.dxf.height *= uniform_scaling_factor
            elif dxftype == 'SHAPE':
                # Scale SHAPE size just by uniform_scaling.
                entity.dxf.size *= uniform_scaling_factor
            elif dxftype == 'HATCH':
                # Non uniform scaling produces incorrect results for boundary paths containing ARC or ELLIPSE segments.
                # Scale HATCH pattern:
                hatch = cast('Hatch', entity)
                if uniform_scaling_factor != 1 and hatch.has_pattern_fill and hatch.pattern is not None:
                    hatch.dxf.pattern_scale *= uniform_scaling_factor
                    # hatch.pattern is already scaled by the stored pattern_scale value
                    hatch.set_pattern_definition(hatch.pattern.as_list(), uniform_scaling_factor)
            else:  # unsupported entity will be ignored
                if only_return_skipped_entities:
                    yield entity
                continue

        if not only_return_skipped_entities:
            yield entity


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
            yield factory.new(dxftype='ARC', dxfattribs=attribs, doc=doc)
        else:
            attribs['start'] = ocs.to_wcs(prev_point)
            attribs['end'] = ocs.to_wcs(point)
            yield factory.new(dxftype='LINE', dxfattribs=attribs, doc=doc)
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
        yield factory.new(dxftype='LINE', dxfattribs=dxfattribs, doc=doc)


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
            yield factory.new(dxftype='3DFACE', dxfattribs=dxfattribs, doc=doc)


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
        yield factory.new(dxftype='3DFACE', dxfattribs=face3d_attribs, doc=doc)
