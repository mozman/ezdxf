#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Sequence, Any, TypeVar, Tuple, Generic
from abc import ABC, abstractmethod
from ezdxf._acis.const import NULL_PTR_NAME
from ezdxf._acis.hdr import AcisHeader

T = TypeVar("T", bound="AbstractEntity")


class AbstractEntity(ABC):
    """Unified query interface for SAT and SAB data."""
    name: str

    def __str__(self):
        return f"{self.name}"

    @property
    def is_null_ptr(self) -> bool:
        """Returns ``True`` if this entity is the ``NULL_PTR`` entity. """
        return self.name == NULL_PTR_NAME

    @abstractmethod
    def find_all(self: T, entity_type: str) -> List[T]:
        """Returns a list of all matching ACIS entities of then given type
        referenced by this entity.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        pass

    @abstractmethod
    def find_first(self: T, entity_type: str) -> T:
        """Returns the first matching ACIS entity referenced by this entity.
        Returns the ``NULL_PTR`` entity if no entity was found.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        ...

    def find_path(self: T, path: str) -> T:
        """Returns the last ACIS entity referenced by an `path`.
        The `path` describes the path to the entity starting form the current
        entity like "lump/shell/face". This is equivalent to::

            face = entity.find_first("lump").find_first("shell").find_first("face")

        Returns ``NULL_PTR`` entity if no entity could be found or if the path
        is invalid.

        Args:
            path: entity types divided by "/" like "lump/shell/face"

        """
        entity = self
        for entity_type in path.split("/"):
            entity = entity.find_first(entity_type)
        return entity

    def find_entities(self: T, names: str) -> List[T]:
        """Find multiple entities of different types. Returns the first
        entity of each type. If a type doesn't exist the ``NULL_PTR`` entity
        is returned for this type::

            coedge, edge = coedge.find_entities("coedge;edge")

        Returns the first coedge and the first edge in the current coedge.
        If no edge entity exist, the edge variable is the ``NULL_PTR`` entity.

        Args:
            names: entity type list as string, separator is ";"

        """
        return [self.find_first(name) for name in names.split(";")]

    @abstractmethod
    def parse_values(self, fmt: str) -> Sequence[Any]:
        """Parse only values from entity data, ignores all entities in front
        or between the data values.

        =========== ==============================
        specifier   data type
        =========== ==============================
        ``f``       float values
        ``v``       vector (3-float) values
        ``i``       integer values
        ``b``       bool values as constant strings like "forward" or "single"
        ``@``       user strings
        ``?``       skip next value
        =========== ==============================

        Args:
            fmt: format specifiers separated by ";"

        """
        pass


class DataLoader(ABC):
    """Data loading interface to create high level AcisEntity data from low
    level AbstractEntity representation.

    """
    version : int = 700

    @abstractmethod
    def has_data(self) -> bool:
        pass

    @abstractmethod
    def read_int(self) -> int:
        pass

    @abstractmethod
    def read_double(self) -> float:
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


class AbstractBuilder(Generic[T]):
    header: AcisHeader
    bodies: List[T]
    entities: List[T]
