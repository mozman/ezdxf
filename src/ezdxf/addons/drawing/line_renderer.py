#  Copyright (c) 2020-2021, Manfred Moitzi
#  License: MIT License
import abc
from typing import Sequence, Optional, Dict, Tuple

from ezdxf.math import Vec3
from .config import Configuration, LinePolicy
from .properties import Properties

PatternKey = Tuple[str, float]


class AbstractLineRenderer(abc.ABC):
    """The line rendering class should get all options from the backend, so a
    change in the backend is also applied by the line renderer e.g. disable
    lineweight or linetype rendering.
    """

    def __init__(self, config: Configuration):
        self._pattern_cache: Dict[PatternKey, Sequence[float]] = dict()
        self._config = config

    @abc.abstractmethod
    def draw_line(
        self, start: Vec3, end: Vec3, properties: Properties, z: float
    ):
        ...

    @abc.abstractmethod
    def draw_path(self, path, properties: Properties, z: float):
        ...

    @property
    def measurement_scale(self) -> float:
        """Returns internal linetype scaling factor."""
        return 1.0

    def pattern(self, properties: Properties) -> Sequence[float]:
        """Get pattern - implements pattern caching."""
        # PatternKey = Tuple[str, float]
        if self._config.line_policy == LinePolicy.SOLID:
            scale = 0.0
        else:
            scale = self.measurement_scale * properties.linetype_scale
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
            min_dash_length = self._config.min_dash_length
            pattern = [
                max(e * scale, min_dash_length)
                for e in properties.linetype_pattern
            ]
            if len(pattern) % 2:
                pattern.pop()
            return pattern

    def lineweight(self, properties: Properties) -> float:
        """Set lineweight_scaling=0 to use a constant minimal lineweight."""
        assert self._config.min_lineweight is not None
        return max(
            properties.lineweight * self._config.lineweight_scaling, self._config.min_lineweight
        )

    def linetype(self, properties: Properties) -> Optional[Sequence[float]]:
        """
        Returns ``None`` if linetype rendering is disabled.
        """
        if self._config.line_policy == LinePolicy.SOLID:
            return None
        else:
            return self.pattern(properties)
