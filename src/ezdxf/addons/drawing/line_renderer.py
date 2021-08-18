#  Copyright (c) 2020-2021, Manfred Moitzi
#  License: MIT License
from typing import Sequence, Optional, Dict, Tuple
import abc
from ezdxf.math import Vec3
from .backend import Backend
from .properties import Properties

PatternKey = Tuple[str, float]


class AbstractLineRenderer:
    """The line rendering class should get all options from the backend, so a
    change in the backend is also applied by the line renderer e.g. disable
    lineweight or linetype rendering.
    """

    def __init__(self, backend: Backend):
        self._pattern_cache: Dict[PatternKey, Sequence[float]] = dict()
        self._backend = backend

    @abc.abstractmethod
    def draw_line(
        self, start: Vec3, end: Vec3, properties: Properties, z: float
    ):
        ...

    @abc.abstractmethod
    def draw_path(self, path, properties: Properties, z: float):
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

    @property
    def measurement(self) -> float:
        return self._backend.measurement

    @property
    def measurement_scale(self) -> float:
        """Returns internal linetype scaling factor."""
        return 1.0

    def pattern(self, properties: Properties) -> Sequence[float]:
        """Get pattern - implements pattern caching."""
        # PatternKey = Tuple[str, float]
        scale = (
            self.measurement_scale
            * self.linetype_scaling
            * properties.linetype_scale
        )
        key: PatternKey = (properties.linetype_name, scale)
        pattern_ = self._pattern_cache.get(key)
        if pattern_ is None:
            pattern_ = self.create_pattern(properties, scale)
            self._pattern_cache[key] = pattern_
        return pattern_

    def create_pattern(
        self, properties: Properties, scale: float
    ) -> Sequence[float]:
        """Returns simplified linetype tuple: on_off_sequence"""
        # only matplotlib needs a different pattern definition
        if len(properties.linetype_pattern) < 2:
            # Do not return None -> None indicates: "not cached"
            return tuple()
        else:
            min_dash_length = self.min_dash_length
            pattern = [
                max(e * scale, min_dash_length)
                for e in properties.linetype_pattern
            ]
            if len(pattern) % 2:
                pattern.pop()
            return pattern

    def lineweight(self, properties: Properties) -> float:
        """Set lineweight_scaling=0 to use a constant minimal lineweight."""
        return max(
            properties.lineweight * self.lineweight_scaling, self.min_lineweight
        )

    def linetype(self, properties: Properties) -> Optional[Sequence[float]]:
        """Set linetype_scaling=0 to disable linetype rendering.

        Returns ``None`` to disable linetype rendering.

        """
        if self.linetype_scaling:
            return self.pattern(properties)
        else:
            return None
