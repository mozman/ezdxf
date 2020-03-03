# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.lldxf.const import DXFStructureError, DXFTypeError

if TYPE_CHECKING:
    from ezdxf.eztypes import Insert, BaseLayout, EntityDB


def explode_block_reference(block_ref: 'Insert', target_layout: 'BaseLayout') -> None:
    if block_ref.doc is None or block_ref.doc.entitydb is None:
        raise DXFStructureError('Block reference has to be assigned to a DXF document.')

    entitydb = block_ref.doc.entitydb
    if entitydb is None:
        raise DXFStructureError('Exploding a block reference requires an entity database.')

    copy_and_transform_entities_to_target_layout(block_ref, target_layout, entitydb)

    # Process attached ATTRIB entities:
    for attrib in block_ref.attribs:
        # Attached ATTRIB entities are already located in the WCS
        target_layout.add_entity(attrib)

    # Unlink attributes else they would be destroyed by deleting the block reference.
    block_ref.attribs = []
    source_layout = block_ref.get_layout()
    if source_layout is not None:
        # Remove and destroy exploded INSERT if assigned to a layout
        source_layout.delete_entity(block_ref)
    else:
        entitydb.delete_entity(block_ref)


def copy_and_transform_entities_to_target_layout(block_ref: 'Insert', target_layout: 'BaseLayout',
                                                 entitydb: 'EntityDB') -> None:
    brcs = block_ref.brcs()
    # Non uniform scaling will produce incorrect results for some entities!
    uniform_scaling = block_ref.dxf.xscale
    block_layout = block_ref.block()
    if block_layout is None:
        raise DXFStructureError(f'Required block definition for "{block_ref.dxf.name}" does not exist.')

    for entity in block_layout:
        dxftype = entity.dxftype()
        if dxftype == 'ATTDEF':  # do not explode ATTDEF entities
            continue

        # Copy entity with all DXF attributes
        try:
            copy = entitydb.duplicate_entity(entity)
        except DXFTypeError:
            continue  # non copyable entities will be ignored

        # Basic transformation from BRCS to WCS
        try:
            copy.transform_to_wcs(brcs)
        except AttributeError:  # entities without 'transform_to_ucs' support will be ignored
            continue

        # Apply DXF attribute scaling:
        # 1. simple entities without properties to scale
        if dxftype in {'LINE', 'POINT', 'LWPOLYLINE', 'POLYLINE', 'MESH', 'ELLIPSE', 'HATCH', 'SPLINE',
                       'SOLID', '3DFACE', 'TRACE', 'IMAGE', 'XLINE', 'RAY', 'TOLERANCE', 'LIGHT', 'HELIX'}:
            pass  # nothing else to do
        elif dxftype in {'CIRCLE', 'ARC'}:
            # simple uniform scaling of radius
            # How to handle non uniform scaling?
            copy.dxf.radius = entity.dxf.radius * uniform_scaling
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
        # assign exploded entities to target layout
        target_layout.add_entity(copy)
