# Purpose: Grouping entities by DXF attributes or a key function.
# Created: 03.02.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License

from ezdxf.lldxf.const import DXFValueError, DXFAttributeError


def groupby(entities, dxfattrib='', key=None):
    """
    Groups a sequence of DXF entities by an DXF attribute like 'layer', returns the result as dict. Just specify
    argument `dxfattrib` OR a `key` function.

    Args:
        entities: sequence of DXF entities to group by a key
        dxfattrib: grouping DXF attribute like 'layer'
        key: key function, which accepts a DXFEntity as argument, returns grouping key of this entity or None for ignore
             this object. Reason for ignoring: a queried DXF attribute is not supported by this entity

    Returns: dict

    """
    if all((dxfattrib, key)):
        raise DXFValueError('Specify a dxfattrib or a key function, but not both.')
    if dxfattrib != '':
        key = lambda entity: entity.get_dxf_attrib(dxfattrib, None)
    if key is None:
        raise DXFValueError('no valid argument found, specify a dxfattrib or a key function, but not both.')

    result = dict()
    for dxf_entity in entities:
        try:
            group_key = key(dxf_entity)
        except DXFAttributeError:  # ignore DXF entities, which do not support all query attributes
            continue
        if group_key is not None:
            group = result.setdefault(group_key, [])
            group.append(dxf_entity)
    return result
