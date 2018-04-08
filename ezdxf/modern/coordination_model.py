# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..dxfentity import DXFEntity
from .graphics import none_subclass, DefSubclass, DXFAttr, DXFAttributes
from ..algebra.matrix44 import Matrix44

coordination_model_subclass = DefSubclass('AcDbNavisworksModel', {
    'definition': DXFAttr(340),  # handle to the AcDbNavisworksModelDef object
})


class CoordinationModel(DXFEntity):
    DXFATTRIBS = DXFAttributes(none_subclass, coordination_model_subclass)

    def get_transformation_data(self):
        """
        Returns: (Transformation Matrix as Matrix44(), Insertion unit factor)

        """
        subclass = self.tags.subclasses[1]
        values = subclass.find_all(40)
        matrix = Matrix44(values[:16])
        factor = 1. if len(values < 17) else values[16]
        return matrix, factor
