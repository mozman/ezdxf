# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, cast, Optional, Tuple
from ezdxf.lldxf.const import DXFValueError

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        DXFObject,
        Dictionary,
        Drawing,
        ObjectsSection,
        EntityDB,
    )


class ObjectCollection:
    def __init__(
        self,
        doc: "Drawing",
        dict_name: str = "ACAD_MATERIAL",
        object_type: str = "MATERIAL",
    ):
        self.doc: "Drawing" = doc
        self.object_type: str = object_type
        self.object_dict: "Dictionary" = doc.rootdict.get_required_dict(
            dict_name
        )

    @property
    def objects(self) -> "ObjectsSection":
        return self.doc.objects

    @property
    def entitydb(self) -> "EntityDB":
        return self.doc.entitydb

    def __iter__(self) -> Iterable[Tuple[str, "DXFObject"]]:
        return self.object_dict.items()

    def __len__(self) -> int:
        return len(self.object_dict)

    def __contains__(self, name: str) -> bool:
        return name in self.object_dict

    def __getitem__(self, name: str) -> "DXFObject":
        return cast("DXFObject", self.object_dict.__getitem__(name))

    def get(
        self, name: str, default: "DXFObject" = None
    ) -> Optional["DXFObject"]:
        """Get object by name.

        Args:
            name: object name as string
            default: default value

        """
        return self.object_dict.get(name, default)  # type: ignore

    def new(self, name: str) -> "DXFObject":
        """Create a new object of type `self.object_type` and store its handle
        in the object manager dictionary.

        Args:
            name: name of new object as string

        Returns:
            new object of type `self.object_type`

        Raises:
            DXFValueError: if object name already exist

        (internal API)

        """
        if name in self.object_dict:
            raise DXFValueError(
                f"{self.object_type} entry {name} already exists."
            )
        return self._new(name, dxfattribs={"name": name})

    def _new(self, name: str, dxfattribs: dict) -> "DXFObject":
        owner = self.object_dict.dxf.handle
        dxfattribs["owner"] = owner
        obj = self.objects.add_dxf_object_with_reactor(
            self.object_type, dxfattribs=dxfattribs
        )
        self.object_dict.add(name, obj)
        return cast("DXFObject", obj)

    def delete(self, name: str) -> None:
        obj = self.object_dict.get(name)
        if obj is not None:
            obj = cast("DXFObject", obj)
            self.object_dict.discard(name)
            self.objects.delete_entity(obj)

    def clear(self) -> None:
        """Delete all entries."""
        self.object_dict.clear()
