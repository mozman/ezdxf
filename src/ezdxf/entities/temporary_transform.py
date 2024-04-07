# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING
import abc

if TYPE_CHECKING:
    from ezdxf.math import Matrix44
    from ezdxf.entities.dxfgfx import DXFEntity


class TemporaryTransformation:
    _matrix: Matrix44 | None = None

    def get_matrix(self) -> Matrix44 | None:
        return self._matrix

    def set_matrix(self, m: Matrix44 | None) -> None:
        self._matrix = m

    def add_matrix(self, m: Matrix44) -> None:
        matrix = self.get_matrix()
        if matrix is not None:
            m = matrix @ m
        self.set_matrix(m)

    @abc.abstractmethod
    def apply_transformation(self, entity: DXFEntity) -> bool: ...
