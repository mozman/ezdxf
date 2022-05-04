#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Sequence, Any
import abc


class AbstractEntity(abc.ABC):
    name: str
    id: int

    def __str__(self):
        return f"{self.name}({self.id})"

    def find_all(self, entity_type: str) -> List["AbstractEntity"]:
        """Returns a list of all matching ACIS entities of then given type
        referenced by this entity.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        ...

    def find_first(self, entity_type: str) -> "AbstractEntity":
        """Returns the first matching ACIS entity referenced by this entity.
        Returns the ``NULL_PTR`` if no entity was found.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        ...

    def find_path(self, path: str) -> "AbstractEntity":
        """Returns the last ACIS entity referenced by an `path`.
        The `path` describes the path to the entity starting form the current
        entity like "lump/shell/face". This is equivalent to::

            face = entity.find_first("lump").find_first("shell").find_first("face")

        Returns ``NULL_PTR`` if no entity could be found or if the path is
        invalid.

        Args:
            path: entity types divided by "/" like "lump/shell/face"

        """
        entity = self
        for entity_type in path.split("/"):
            entity = entity.find_first(entity_type)
        return entity

    def find_entities(self, names: str) -> List["AbstractEntity"]:
        """Find multiple entities of different types. Returns the first
        entity of each type. If a type doesn't exist a ``NULL_PTR`` is
        returned for this type::

            coedge, edge = coedge.find_entities("coedge;edge")

        Returns the first coedge and the first edge in the current coedge.
        If no edge entity exist, the edge variable is the ``NULL_PTR``.

        Args:
            names: entity type list as string, separator is ";"

        """
        return [self.find_first(name) for name in names.split(";")]

    def parse_values(self, fmt: str) -> Sequence[Any]:
        """Parse only values from entity data, ignores all entities in front
        or between the data values.

        =========== ==============================
        specifier   data type
        =========== ==============================
        ``f``       float values
        ``v``       vector (3-float) values
        ``i``       integer values
        ``s``       string constants like "forward"
        ``?``       skip (unknown) value
        =========== ==============================

        Args:
            fmt: format specifiers separated by ";"

        """
        pass
