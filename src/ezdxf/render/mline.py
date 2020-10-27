#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

from typing import TYPE_CHECKING, List
from ezdxf.entities import factory
from ezdxf.math import Vector
import logging

if TYPE_CHECKING:
    from ezdxf.entities import MLine, DXFGraphic

__all__ = ['virtual_entities']

logger = logging.getLogger('ezdxf')


# The MLINE geometry stored in vertices, is the final geometry,
# scaling factor, justification and MLineStyle settings are already
# applied.

def _dxfattribs(mline):
    attribs = mline.graphic_properties()
    # True color value of MLINE is ignored by CAD applications:
    if 'true_color' in attribs:
        del attribs['true_color']
    return attribs


def virtual_entities(mline: 'MLine') -> List['DXFGraphic']:
    """ Yields 'virtual' parts of MLINE as LINE, ARC and HATCH entities.

    This entities are located at the original positions, but are not stored
    in the entity database, have no handle and are not assigned to any
    layout.
    """

    def filling():
        hatch = factory.new('HATCH')
        hatch.dxf.color = style.dxf.fill_color
        return hatch

    def start_cap():
        return []

    def lines():
        prev = None
        _lines = []
        attribs = _dxfattribs(mline)

        for miter in miter_points:
            if prev is not None:
                for index, element in enumerate(style.elements):
                    attribs['start'] = prev[index]
                    attribs['end'] = miter[index]
                    attribs['color'] = element.color
                    attribs['linetype'] = element.linetype
                    _lines.append(factory.new(
                        'LINE', dxfattribs=attribs, doc=doc))
            prev = miter
        return _lines

    def end_cap():
        return []

    entities = []
    if not mline.is_alive or mline.doc is None or len(mline.vertices) < 2:
        return entities

    style = mline.style
    if style is None:
        return entities

    doc = mline.doc
    element_count = len(style.elements)
    closed = mline.is_closed
    bottom_index, top_index = style.border_indices()
    bottom_border: List[Vector] = []
    top_border: List[Vector] = []
    miter_points: List[List[Vector]] = []

    for vertex in mline.vertices:
        offsets = vertex.line_params
        if len(offsets) != element_count:
            logger.debug(
                f'Invalid line parametrization for vertex {len(miter_points)} '
                f'in {str(mline)}.'
            )
            return entities
        location = vertex.location
        miter_direction = vertex.miter_direction
        miter = []
        for offset in offsets:
            try:
                length = offset[0]
            except IndexError:  # DXFStructureError?
                length = 0
            miter.append(location + miter_direction * length)
        miter_points.append(miter)
        top_border.append(miter[top_index])
        bottom_border.append(miter[bottom_index])

    if closed:
        miter_points.append(miter_points[0])
        top_border.append(top_border[0])
        bottom_border.append(bottom_border[0])

    entities.extend(start_cap())
    entities.extend(lines())
    entities.extend(end_cap())
    if style.get_flag_state(style.FILL):
        entities.insert(0, filling())

    return entities
