# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.algebra.ucs import UCS, PassTroughUCS

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType, DimStyle, Dimension


class DimensionBase:
    def __init__(self, dimension: 'Dimension', dimstyle: 'DimStyle', layout: 'GenericLayoutType' = None, ucs=None):
        self.layout = layout
        self.dimstyle = dimstyle
        self.dimension = dimension
        self.ucs = ucs

    def render(self, layout: 'GenericLayoutType' = None, ucs: 'UCS' = None):
        if layout:
            self.layout = layout

        if ucs:
            self.ucs = ucs

        if self.ucs is None:
            self.ucs = PassTroughUCS()


class LinearDimension(DimensionBase):
    def render(self, layout: 'GenericLayoutType' = None, ucs: 'UCS' = None):
        super().render(layout, ucs)


def render_linear_dimension(dimension: 'Dimension', dimstyle: 'DimStyle', layout: 'GenericLayoutType',
                            ucs: 'UCS' = None):
    renderer = LinearDimension(dimension, dimstyle, layout, ucs)
    renderer.render()
