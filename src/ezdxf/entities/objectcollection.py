# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterator, cast, Optional, Tuple
from ezdxf.lldxf.const import DXFValueError, DXFKeyError, INVALID_NAME_CHARACTERS
from ezdxf.lldxf.validator import make_table_key, is_valid_table_name

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        DXFObject,
        Dictionary,
        Drawing,
    )


def validate_name(name: str) -> str:
    name = name[:255]
    if not is_valid_table_name(name):
        raise DXFValueError(
            f"table name '{name}' contains invalid characters: {INVALID_NAME_CHARACTERS}"
        )
    return name


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

    def __iter__(self) -> Iterator[Tuple[str, "DXFObject"]]:
        return self.object_dict.items()

    def __len__(self) -> int:
        return len(self.object_dict)

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None

    def __getitem__(self, name: str) -> "DXFObject":
        entry = self.get(name)
        if entry is None:
            raise DXFKeyError(name)
        return cast("DXFObject", entry)

    def is_unique_name(self, name: str) -> bool:
        name = make_table_key(name)
        for entry_name in self.object_dict.keys():
            if make_table_key(entry_name) == name:
                return False
        return True

    def get(
        self, name: str, default: "DXFObject" = None
    ) -> Optional["DXFObject"]:
        """Get object by name. Object collection entries are case insensitive.

        Args:
            name: object name as string
            default: default value

        """
        name = make_table_key(name)
        for entry_name, obj in self.object_dict.items():
            if make_table_key(entry_name) == name:
                return obj
        return default

    def new(self, name: str) -> "DXFObject":
        """Create a new object of type `self.object_type` and store its handle
        in the object manager dictionary.  Object collection entry names are
        case insensitive and limited to 255 characters.

        Args:
            name: name of new object as string

        Returns:
            new object of type `self.object_type`

        Raises:
            DXFValueError: if object name already exist or is invalid

        (internal API)

        """
        name = validate_name(name)
        if not self.is_unique_name(name):
            raise DXFValueError(
                f"{self.object_type} entry {name} already exists."
            )
        return self._new(name, dxfattribs={"name": name})

    def duplicate_entry(self, name: str, new_name: str) -> "DXFObject":
        """Returns a new table entry `new_name` as copy of `name`,
        replaces entry `new_name` if already exist.

        Raises:
             DXFValueError: `name` does not exist

        """
        entry = self.get(name)
        if entry is None:
            raise DXFValueError(f"entry '{name}' does not exist")
        new_name = validate_name(new_name)
        # remove existing entry
        existing_entry = self.get(new_name)
        if existing_entry is not None:
            self.delete(new_name)

        entitydb = self.doc.entitydb
        if entitydb:
            new_entry = entitydb.duplicate_entity(entry)
        else:  # only for testing!
            new_entry = entry.copy()
        if new_entry.dxf.is_supported("name"):
            new_entry.dxf.name = new_name
        self.object_dict.add(new_name, new_entry)  # type: ignore
        owner_handle = self.object_dict.dxf.handle
        new_entry.dxf.owner = owner_handle
        new_entry.set_reactors([owner_handle])
        return new_entry  # type: ignore

    def _new(self, name: str, dxfattribs: dict) -> "DXFObject":
        objects = self.doc.objects
        assert objects is not None

        owner = self.object_dict.dxf.handle
        dxfattribs["owner"] = owner
        obj = objects.add_dxf_object_with_reactor(
            self.object_type, dxfattribs=dxfattribs
        )
        self.object_dict.add(name, obj)
        return cast("DXFObject", obj)

    def delete(self, name: str) -> None:
        objects = self.doc.objects
        assert objects is not None

        obj = self.get(name)  # case insensitive
        if obj is not None:
            obj = cast("DXFObject", obj)
            # The underlying DICTIONARY is not case insensitive implemented,
            # get real object name if available
            if obj.dxf.is_supported("name"):
                name = obj.dxf.get("name", name)
            self.object_dict.discard(name)
            objects.delete_entity(obj)

    def clear(self) -> None:
        """Delete all entries."""
        self.object_dict.clear()
