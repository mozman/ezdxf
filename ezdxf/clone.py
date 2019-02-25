# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from copy import deepcopy


def clone(entity):
    copier = getattr(entity, 'clone', None)
    if copier:
        return copier()
    else:
        return deepcopy(entity)
