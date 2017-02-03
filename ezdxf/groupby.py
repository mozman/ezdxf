# Purpose: Grouping entities by DXF attributes or a key function.
# Created: 03.02.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License

from collections import defaultdict, Mapping


class GroupByResult(Mapping):
    def __init__(self):
        self.groups = defaultdict(list)

    def __len__(self):
        return len(self.groups)

    def __contains__(self, key):
        return key in self.groups

    def __getitem__(self, key):
        """

        :param key: selection key
        :return:
        """
        if key in self.groups:  # defaultdict returns ALWAYS an item
            return self.groups[key]
        else:
            raise KeyError(key)

    def __iter__(self):
        return iter(self.groups)

    def _add_entity(self, key, entity):
        self.groups[key].append(entity)


def groupby(entities, dxfattrib='', key=None):
    """
    Groups a sequence of DXF entities by an DXF attribute like 'layer', the result container :class:`GroupByResult` is
    a mapping (just readable dict). Just specify argument `dxfattrib` OR a `key` function.

    Args:
        entities: sequence of DXF entities to group by a key
        dxfattrib: grouping DXF attribute like 'layer'
        key: key function, which accepts a DXFEntity as argument, returns grouping key of this entity or None for ignore
             this object. Reason for ignoring: a queried DXF attribute is not supported by this entity

    Returns:
        GroupByResult
    """
    if all((dxfattrib, key)):
        raise ValueError('Specify a dxfattrib or a key, but not both.')
    if dxfattrib != '':
        key = lambda entity: entity.get_dxf_attrib(dxfattrib, None)
    if key is None:
        raise ValueError('no valid argument found, specify a dxfattrib or a key, but not both.')

    result = GroupByResult()
    for dxf_entity in entities:
        try:
            group_key = key(dxf_entity)
        except AttributeError:  # DXF entities, which do not support query attributes
            continue
        if group_key is not None:
            result._add_entity(group_key, dxf_entity)

    return result