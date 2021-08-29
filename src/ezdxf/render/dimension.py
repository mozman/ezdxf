# Copyright (c) 2018-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.math import UCS
from ezdxf.lldxf.const import DXFValueError
from ezdxf.entities.dimstyleoverride import DimStyleOverride

from .dim_linear import LinearDimension
from .dim_radius import RadiusDimension
from .dim_diameter import DiameterDimension

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension, BaseDimensionRenderer


class DimensionRenderer:
    def dispatch(
        self, override: "DimStyleOverride", ucs: "UCS" = None
    ) -> "BaseDimensionRenderer":
        dimension = override.dimension
        dim_type = dimension.dimtype

        if dim_type in (0, 1):
            return self.linear(dimension, ucs, override)
        elif dim_type == 2:
            return self.angular(dimension, ucs, override)
        elif dim_type == 3:
            return self.diameter(dimension, ucs, override)
        elif dim_type == 4:
            return self.radius(dimension, ucs, override)
        elif dim_type == 5:
            return self.angular3p(dimension, ucs, override)
        elif dim_type == 6:
            return self.ordinate(dimension, ucs, override)
        else:
            raise DXFValueError(f"Unknown DIMENSION type: {dim_type}")

    def linear(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        """Call renderer for linear dimension lines: horizontal, vertical and rotated"""
        return LinearDimension(dimension, ucs, override)

    def angular(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        raise NotImplementedError()

    def diameter(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        """Call renderer for diameter dimension"""
        return DiameterDimension(dimension, ucs, override)

    def radius(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        """Call renderer for radius dimension"""
        return RadiusDimension(dimension, ucs, override)

    def angular3p(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        raise NotImplementedError()

    def ordinate(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        raise NotImplementedError()
