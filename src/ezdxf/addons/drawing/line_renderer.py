#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import abc
from ezdxf.math import Vector
from .backend import Backend
from .properties import Properties


class AbstractLineRenderer:
    """ The line rendering class should get all options from the backend, so a
    change in the backend is also applied by the line renderer e.g. disable
    lineweight or linetype rendering.
    """

    def __init__(self, backend: Backend):
        self._pattern_cache = dict()
        self._backend = backend

    @abc.abstractmethod
    def draw_line(self, start: Vector, end: Vector,
                  properties: Properties, z: float):
        ...

    @abc.abstractmethod
    def draw_path(self, path, properties: Properties, z: float):
        ...

    @abc.abstractmethod
    def create_pattern(self, properties: Properties, scale: float):
        ...

    @property
    def linetype_scaling(self) -> float:
        return self._backend.linetype_scaling

    @property
    def lineweight_scaling(self) -> float:
        return self._backend.lineweight_scaling

    @property
    def min_lineweight(self) -> float:
        return self._backend.min_lineweight

    @property
    def min_dash_length(self) -> float:
        return self._backend.min_dash_length

    @property
    def max_flattening_distance(self) -> float:
        return self._backend.max_flattening_distance

    def pattern(self, properties: Properties):
        """ Get pattern - implements pattern caching. """
        scale = self.linetype_scaling * properties.linetype_scale
        key = (properties.linetype_name, scale)
        pattern_ = self._pattern_cache.get(key)
        if pattern_ is None:
            pattern_ = self.create_pattern(properties, scale)
            self._pattern_cache[key] = pattern_
        return pattern_

    def lineweight(self, properties: Properties) -> float:
        """ Set lineweight_scaling=0 to use a constant minimal lineweight. """
        return max(
            properties.lineweight * self.lineweight_scaling,
            self.min_lineweight
        )

    def linetype(self, properties: Properties):
        """ Set linetype_scaling=0 to disable linetype rendering.

        Returns ``None`` to disable linetzype rendering.

        """
        if self.linetype_scaling:
            return self.pattern(properties)
        else:
            return None
