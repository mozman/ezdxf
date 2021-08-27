# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    Optional,
    List,
    Dict,
    cast,
    Union,
)
from collections import OrderedDict
import logging

from ezdxf.lldxf import const, validator
from ezdxf.entities.table import TableHead
from ezdxf.entities import factory

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter,
        EntityDB,
        Drawing,
        DXFEntity,
        Layer,
        Linetype,
        Textstyle,
        VPort,
        View,
        AppID,
        UCSTableEntry,
        BlockRecord,
        DimStyle,
    )

logger = logging.getLogger("ezdxf")

TABLENAMES = {
    "LAYER": "LAYERS",
    "LTYPE": "LINETYPES",
    "APPID": "APPIDS",
    "DIMSTYLE": "DIMSTYLES",
    "STYLE": "STYLES",
    "UCS": "UCS",
    "VIEW": "VIEWS",
    "VPORT": "VIEWPORTS",
    "BLOCK_RECORD": "BLOCK_RECORDS",
}


def tablename(dxfname: str) -> str:
    """Translate DXF-table-name to attribute-name. ('LAYER' -> 'LAYERS')"""
    name = dxfname.upper()
    name = TABLENAMES.get(name, name + "S")
    return name


def table_key(name: str) -> str:
    """Unified table entry key."""
    # see also comments for ezdxf.lldxf.validator.is_valid_table_name()
    if not isinstance(name, str):
        raise TypeError("Name has to be a string.")
    return name.lower()  # table key is lower case


class Table:
    def __init__(
        self, doc: "Drawing" = None, entities: Iterable["DXFEntity"] = None
    ):
        self.doc = doc
        self.entries: Dict[str, DXFEntity] = OrderedDict()
        self._head = TableHead()
        if entities is not None:
            self.load(iter(entities))

    def load(self, entities: Iterator["DXFEntity"]) -> None:
        """Loading interface. (internal API)"""
        table_head = next(entities)
        if isinstance(table_head, TableHead):
            self._head = table_head
        else:
            raise const.DXFStructureError(
                "Critical structure error in TABLES section."
            )
        expected_entry_dxftype = self.entry_dxftype
        for table_entry in entities:
            if table_entry.dxftype() == expected_entry_dxftype:
                self._append(table_entry)
            else:
                logger.warning(
                    f"Ignored invalid DXF entity type '{table_entry.dxftype()}'"
                    f" in table '{self.name}'."
                )

    @classmethod
    def new_table(cls, name: str, handle: str, doc: "Drawing") -> "Table":
        """Create new table. (internal API)"""
        table = cls(doc)
        table._set_head(name, handle)
        return table

    def _set_head(self, name: str, handle: str = None) -> None:
        self._head = TableHead.new(
            handle, owner="0", dxfattribs={"name": name}, doc=self.doc
        )

    @property
    def head(self):
        """Returns table head entry."""
        return self._head

    @property
    def entry_dxftype(self) -> str:
        return self._head.dxf.name

    @staticmethod
    def key(name: str) -> str:
        """Unified table entry key."""
        return table_key(name)

    @property
    def name(self) -> str:
        """Table name like ``layers``."""
        return tablename(self.entry_dxftype)

    def has_entry(self, name: str) -> bool:
        """Returns ``True`` if an table entry `name` exist."""
        return self.key(name) in self.entries

    __contains__ = has_entry

    def __len__(self) -> int:
        """Count of table entries."""
        return len(self.entries)

    def __iter__(self) -> Iterator["DXFEntity"]:
        """Iterable of all table entries."""
        for e in self.entries.values():
            if e.is_alive:
                yield e

    def new(self, name: str, dxfattribs: dict = None) -> "DXFEntity":
        """Create a new table entry `name`.

        Args:
            name: name of table entry, case insensitive
            dxfattribs: additional DXF attributes for table entry

        """
        if self.has_entry(name):
            raise const.DXFTableEntryError(
                f"{self._head.dxf.name} {name} already exists!"
            )
        dxfattribs = dxfattribs or {}
        dxfattribs["name"] = name
        dxfattribs["owner"] = self._head.dxf.handle
        return self.new_entry(dxfattribs)

    def get(self, name: str) -> "DXFEntity":
        """Get table entry `name` (case insensitive).
        Raises :class:`DXFValueError` if table entry does not exist.
        """
        key = self.key(name)
        entry = self.entries.get(key, None)
        if entry:
            return entry
        else:
            raise const.DXFTableEntryError(name)

    def remove(self, name: str) -> None:
        """Removes table entry `name`. Raises :class:`DXFValueError`
        if table-entry does not exist.
        """
        key = self.key(name)
        entry = self.get(name)
        self.entitydb.delete_entity(entry)
        self.discard(key)

    def duplicate_entry(self, name: str, new_name: str) -> "DXFEntity":
        """Returns a new table entry `new_name` as copy of `name`,
        replaces entry `new_name` if already exist.

        Raises:
             DXFValueError: `name` does not exist

        """
        entry = self.get(name)
        entitydb = self.entitydb
        if entitydb:
            new_entry = entitydb.duplicate_entity(entry)
        else:  # only for testing!
            new_entry = entry.copy()
        new_entry.dxf.name = new_name
        self._append(new_entry)
        return new_entry

    def discard(self, name: str) -> None:
        """Remove table entry without destroying object. (internal API)"""
        del self.entries[self.key(name)]

    def replace(self, name: str, entry: "DXFEntity") -> None:
        """Replace table entry `name` by new `entry`. (internal API)"""
        self.discard(name)
        self._append(entry)

    @property
    def entitydb(self) -> "EntityDB":
        return self.doc.entitydb  # type: ignore

    def new_entry(self, dxfattribs: dict) -> "DXFEntity":
        """Create and add new table-entry of type 'self.entry_dxftype'.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        entry = factory.create_db_entry(
            self._head.dxf.name, dxfattribs, self.doc  # type: ignore
        )
        self._append(entry)
        return entry

    def _append(self, entry: "DXFEntity") -> None:
        """Add a table entry, replaces existing entries with same name.
        (internal API).
        """
        assert entry.dxftype() == self.entry_dxftype
        self.entries[self.key(entry.dxf.name)] = entry

    def add_entry(self, entry: "DXFEntity") -> None:
        """Add a table `entry`, created by other object than this table.
        (internal API)
        """
        if entry.dxftype() != self.entry_dxftype:
            raise const.DXFTypeError(
                f"Invalid table entry type {entry.dxftype()} "
                f"for table {self.name}"
            )
        name = entry.dxf.name
        if self.has_entry(name):
            raise const.DXFTableEntryError(
                f"{self._head.dxf.name} {name} already exists!"
            )
        entry.doc = self.doc
        entry.dxf.owner = self._head.dxf.handle
        self._append(entry)

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        """Export DXF representation. (internal API)"""

        def prologue():
            self.update_owner_handles()
            # The table head itself has no owner and is therefore always '0':
            self._head.dxf.owner = "0"
            self._head.dxf.count = len(self)
            self._head.export_dxf(tagwriter)

        def content():
            for entry in self.entries.values():
                # VPORT
                if isinstance(entry, list):
                    for e in entry:
                        e.export_dxf(tagwriter)
                else:
                    entry.export_dxf(tagwriter)

        def epilogue():
            tagwriter.write_tag2(0, "ENDTAB")

        prologue()
        content()
        epilogue()

    def update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entry in self.entries.values():
            entry.dxf.owner = owner_handle

    def set_handle(self, handle: str):
        """Set new `handle` for table, updates also :attr:`owner` tag of table
        entries. (internal API)
        """
        if self._head.dxf.handle is None:
            self._head.dxf.handle = handle
            self.update_owner_handles()


class LayerTable(Table):
    def new_entry(self, dxfattribs: dict) -> "DXFEntity":
        layer = cast("Layer", super().new_entry(dxfattribs))
        if self.doc:
            layer.set_required_attributes()
        return layer

    def add(
        self,
        name: str,
        *,
        color: int = const.BYLAYER,
        true_color: int = None,
        linetype: str = "Continuous",
        lineweight: int = const.LINEWEIGHT_BYLAYER,
        plot: bool = True,
        dxfattribs: Dict = None,
    ) -> "Layer":
        """Add a new :class:`~ezdxf.entities.Layer`.

        Args:
            name (str): layer name
            color (int): :ref:`ACI` value, default is BYLAYER
            true_color (int): true color value, use :func:`ezdxf.rgb2int` to
                create ``int`` values from RGB values
            linetype (str): line type name, default is "Continuous"
            lineweight (int): line weight, default is BYLAYER
            plot (bool): plot layer as bool, default is ``True``
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        if validator.is_valid_aci_color(color):
            dxfattribs["color"] = color
        else:
            raise const.DXFValueError(f"invalid color: {color}")
        dxfattribs["linetype"] = linetype
        if validator.is_valid_lineweight(lineweight):
            dxfattribs["lineweight"] = lineweight
        else:
            raise const.DXFValueError(f"invalid lineweight: {lineweight}")
        if true_color is not None:
            dxfattribs["true_color"] = int(true_color)
        dxfattribs["plot"] = int(plot)
        return self.new(name, dxfattribs)  # type: ignore


class LineTypeTable(Table):
    def new_entry(self, dxfattribs: dict) -> "DXFEntity":
        pattern = dxfattribs.pop("pattern", [0.0])
        length = dxfattribs.pop("length", 0)  # required for complex types
        ltype = cast("Linetype", super().new_entry(dxfattribs))
        ltype.setup_pattern(pattern, length)
        return ltype

    def add(
        self,
        name: str,
        pattern: Union[List[float], str],
        *,
        description: str = "",
        length: float = 0.0,
        dxfattribs: Dict = None,
    ) -> "Linetype":
        """Add a new line type entry. The simple line type pattern is a list of
        floats :code:`[total_pattern_length, elem1, elem2, ...]`
        where an element > 0 is a line, an element < 0 is a gap and  an
        element == 0.0 is a dot. The definition for complex line types are
        strings, like: ``'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'``
        similar to the line type definitions stored in the line definition
        `.lin` files, for more information see the tutorial about complex line
        types. Be aware that not many CAD applications and DXF viewers support
        complex linetypes.

        .. seealso::

            - `Tutorial for simple line types <https://ezdxf.mozman.at/docs/tutorials/linetypes.html>`_
            - `Tutorial for complex line types <https://ezdxf.mozman.at/docs/tutorials/linetypes.html#tutorial-for-complex-linetypes>`_

        Args:
            name (str): line type  name
            pattern: line type pattern as list of floats or as a string
            description (str): line type description, optional
            length (float): total pattern length, only for complex line types required
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs.update(
            {
                "name": name,
                "description": str(description),
                "pattern": pattern,
                "length": float(length),
            }
        )
        return self.new_entry(dxfattribs)  # type: ignore


class StyleTable(Table):
    def add(
        self, name: str, *, font: str, dxfattribs: Dict = None
    ) -> "Textstyle":
        """Add a new text style entry for TTF fonts. The entry must not yet
        exist, otherwise an :class:`DXFTableEntryError` exception will be
        raised.

        Finding the TTF font files is the task of the DXF viewer and each
        viewer is different (hint: support files).

        Args:
            name (str): text style name
            font (str): TTF font file name like "Arial.ttf", the real font file
                name from the file system is required and remember only Windows
                is case insensitive.
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs.update(
            {
                "name": name,
                "font": str(font),
                "last_height": 2.5,  # maybe required by AutoCAD
            }
        )
        return self.new_entry(dxfattribs)  # type: ignore

    def add_shx(self, shx_file: str, *, dxfattribs: Dict = None) -> "Textstyle":
        """Add a new shape font (SHX file) entry. These are special text style
        entries and have no name. The entry must not yet exist, otherwise an
        :class:`DXFTableEntryError` exception will be raised.

        Finding the SHX files is the task of the DXF viewer and each
        viewer is different (hint: support files).

        Args:
            shx_file (str): shape file name like "gdt.shx"
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        if self.find_shx(shx_file) is not None:
            raise const.DXFTableEntryError(
                f"{self._head.dxf.name} shape file entry for "
                f"'{shx_file}' already exists!"
            )

        dxfattribs = dict(dxfattribs or {})
        dxfattribs.update(
            {
                "name": "",  # shape file entry has no name
                "flags": 1,  # shape file flag
                "font": shx_file,
                "last_height": 2.5,  # maybe required by AutoCAD
            }
        )
        return self.new_entry(dxfattribs)  # type: ignore

    def get_shx(self, shx_file: str) -> "Textstyle":
        """Get existing entry for a shape file (SHX file), or create a new
        entry.

        Finding the SHX files is the task of the DXF viewer and each
        viewer is different (hint: support files).

        Args:
            shx_file (str): shape file name like "gdt.shx"

        """
        shape_file = self.find_shx(shx_file)
        if shape_file is None:
            return self.add_shx(shx_file)
        return shape_file

    def find_shx(self, shx_file: str) -> Optional["Textstyle"]:
        """Find the shape file (SHX file) text style table entry, by a case
        insensitive search.

        A shape file table entry has no name, so you have to search by the
        font attribute.

        Args:
            shx_file (str): shape file name like "gdt.shx"

        """
        lower_name = shx_file.lower()
        for entry in iter(self):
            if entry.dxf.font.lower() == lower_name:
                return entry  # type: ignore
        return None


class ViewportTable(Table):
    # Viewport-Table can have multiple entries with same name
    # each table entry is a list of VPORT entries

    def new(self, name: str, dxfattribs: dict = None) -> "DXFEntity":
        """Create a new table entry."""
        dxfattribs = dxfattribs or {}
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)

    def add(self, name: str, *, dxfattribs: Dict = None) -> "VPort":
        """Add a new modelspace viewport entry. A modelspace viewport
        configuration can consist of multiple viewport entries with the same
        name.

        Args:
            name (str): viewport name, multiple entries possible
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)  # type: ignore

    def remove(self, name: str) -> None:
        """Remove table-entry from table and entitydb by name."""
        key = self.key(name)
        entries = cast(List["DXFEntity"], self.get(name))
        for entry in entries:
            self.entitydb.delete_entity(entry)
        del self.entries[key]

    def __iter__(self) -> Iterator["DXFEntity"]:
        for entries in self.entries.values():
            yield from iter(entries)  # type: ignore

    def _flatten(self) -> Iterator["DXFEntity"]:
        for entries in self.entries.values():
            yield from iter(entries)  # type: ignore

    def __len__(self):
        # calling __iter__() invokes recursion!
        return len(list(self._flatten()))

    def new_entry(self, dxfattribs: dict) -> "DXFEntity":
        """Create and add new table-entry of type 'self.entry_dxftype'.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        entry = factory.create_db_entry(
            self._head.dxf.name, dxfattribs, self.doc  # type: ignore
        )
        self._append(entry)
        return entry

    def duplicate_entry(self, name: str, new_name: str) -> "DXFEntity":
        raise NotImplementedError()

    def _append(self, entry: "DXFEntity") -> None:
        key = self.key(entry.dxf.name)
        if key in self.entries:
            self.entries[key].append(entry)  # type: ignore
        else:
            self.entries[key] = [entry]  # type: ignore # store list of VPORT

    def update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entries in self.entries.values():
            for entry in entries:  # type: ignore
                entry.dxf.owner = owner_handle

    def get_config(self, name: str) -> List["DXFEntity"]:
        """Returns a list of :class:`~ezdxf.entities.VPort` objects, for
        the multi-viewport configuration `name`.
        """
        try:
            return self.entries[self.key(name)]  # type: ignore
        except KeyError:
            raise const.DXFTableEntryError(name)

    def delete_config(self, name: str) -> None:
        """Delete all :class:`~ezdxf.entities.VPort` objects of the
        multi-viewport configuration `name`.
        """
        self.remove(name)


class AppIDTable(Table):
    def add(self, name: str, *, dxfattribs: Dict = None) -> "AppID":
        """Add a new appid table entry.

        Args:
            name (str): appid name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)  # type: ignore


class ViewTable(Table):
    def add(self, name: str, *, dxfattribs: Dict = None) -> "View":
        """Add a new view table entry.

        Args:
            name (str): view name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)  # type: ignore


class BlockRecordTable(Table):
    def add(self, name: str, *, dxfattribs: Dict = None) -> "BlockRecord":
        """Add a new block record table entry.

        Args:
            name (str): block record name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)  # type: ignore


class DimStyleTable(Table):
    def add(self, name: str, *, dxfattribs: Dict = None) -> "DimStyle":
        """Add a new dimension style table entry.

        Args:
            name (str): dimension style name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)  # type: ignore


class UCSTable(Table):
    def add(self, name: str, *, dxfattribs: Dict = None) -> "UCSTableEntry":
        """Add a new UCS table entry.

        Args:
            name (str): UCS name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)  # type: ignore
