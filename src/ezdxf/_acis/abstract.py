#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import List, TypeVar, Tuple, Generic, TYPE_CHECKING
from abc import ABC, abstractmethod
from ezdxf._acis.const import NULL_PTR_NAME, MIN_EXPORT_VERSION
from ezdxf._acis.hdr import AcisHeader

if TYPE_CHECKING:
    from .entities import AcisEntity


T = TypeVar("T", bound="AbstractEntity")


class AbstractEntity(ABC):
    """Unified query interface for SAT and SAB data."""

    name: str

    def __str__(self):
        return f"{self.name}"

    @property
    def is_null_ptr(self) -> bool:
        """Returns ``True`` if this entity is the ``NULL_PTR`` entity."""
        return self.name == NULL_PTR_NAME


class DataLoader(ABC):
    """Data loading interface to create high level AcisEntity data from low
    level AbstractEntity representation.

    """

    version: int = 700

    @abstractmethod
    def has_data(self) -> bool:
        pass

    @abstractmethod
    def read_int(self, skip_sat: int = None) -> int:
        """There are sometimes additional int values in SAB files which are
        not present in SAT files, maybe reference counters e.g. vertex, coedge.
        """
        pass

    @abstractmethod
    def read_double(self) -> float:
        pass

    @abstractmethod
    def read_interval(self) -> float:
        pass

    @abstractmethod
    def read_vec3(self) -> Tuple[float, float, float]:
        pass

    @abstractmethod
    def read_bool(self, true: str, false: str) -> bool:
        pass

    @abstractmethod
    def read_str(self) -> str:
        pass

    @abstractmethod
    def read_ptr(self) -> AbstractEntity:
        pass


class DataExporter(ABC):
    version: int = MIN_EXPORT_VERSION


class AbstractBuilder(Generic[T]):
    header: AcisHeader
    bodies: List[T]
    entities: List[T]


class EntityExporter:
    version: int = MIN_EXPORT_VERSION

    @abstractmethod
    def export(self, entity: AcisEntity) -> None:
        pass
