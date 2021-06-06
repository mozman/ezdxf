# Copyright (c) 2017-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    Iterable,
    List,
    Tuple,
    Set,
    TextIO,
    Any,
    Dict,
    Optional,
    Callable,
    cast,
)
import sys
from enum import IntEnum
from itertools import permutations
from ezdxf.lldxf import const, validator
from ezdxf.entities import factory, DXFEntity
from ezdxf.math import NULLVEC, Vec3, Matrix44
from ezdxf.sections.table import table_key

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        DXFEntity,
        Drawing,
        DXFGraphic,
        BlocksSection,
        EntityDB,
        Dimension,
        GenericLayoutType,
    )

__all__ = ["Auditor", "AuditError", "audit", "BlockCycleDetector"]


class AuditError(IntEnum):
    # DXF structure errors:
    MISSING_REQUIRED_ROOT_DICT_ENTRY = 1
    DUPLICATE_TABLE_ENTRY_NAME = 2
    POINTER_TARGET_NOT_EXIST = 3
    TABLE_NOT_FOUND = 4
    MISSING_SECTION_TAG = 5
    MISSING_SECTION_NAME_TAG = 6
    MISSING_ENDSEC_TAG = 7
    FOUND_TAG_OUTSIDE_SECTION = 8
    REMOVED_UNSUPPORTED_SECTION = 9
    REMOVED_UNSUPPORTED_TABLE = 10

    UNDEFINED_LINETYPE = 100
    UNDEFINED_DIMENSION_STYLE = 101
    UNDEFINED_TEXT_STYLE = 102
    UNDEFINED_BLOCK = 103
    INVALID_BLOCK_REFERENCE_CYCLE = 104
    REMOVE_EMPTY_GROUP = 105
    GROUP_ENTITIES_IN_DIFFERENT_LAYOUTS = 106
    MISSING_REQUIRED_SEQEND = 107
    ORPHANED_LAYOUT_ENTITY = 108
    ORPHANED_PAPER_SPACE_BLOCK_RECORD_ENTITY = 109
    INVALID_TABLE_HANDLE = 110
    DECODING_ERROR = 111
    CREATED_MISSING_OBJECT = 112
    RESET_MLINE_STYLE = 113

    # DXF entity property errors:
    INVALID_ENTITY_HANDLE = 201
    INVALID_OWNER_HANDLE = 202
    INVALID_LAYER_NAME = 203
    INVALID_COLOR_INDEX = 204
    INVALID_LINEWEIGHT = 205
    INVALID_MLINESTYLE_HANDLE = 206

    # DXF entity geometry or content errors:
    INVALID_EXTRUSION_VECTOR = 210
    INVALID_MAJOR_AXIS = 211
    INVALID_VERTEX_COUNT = 212
    INVALID_DICTIONARY_ENTRY = 213
    INVALID_CHARACTER = 214
    INVALID_MLINE_VERTEX = 215
    INVALID_MLINESTYLE_ELEMENT_COUNT = 216
    INVALID_SPLINE_DEFINITION = 217
    INVALID_SPLINE_CONTROL_POINT_COUNT = 218
    INVALID_SPLINE_FIT_POINT_COUNT = 219
    INVALID_SPLINE_KNOT_VALUE_COUNT = 220
    INVALID_SPLINE_WEIGHT_COUNT = 221
    INVALID_DIMENSION_GEOMETRY_LOCATION = 222


REQUIRED_ROOT_DICT_ENTRIES = ("ACAD_GROUP", "ACAD_PLOTSTYLENAME")


class ErrorEntry:
    def __init__(
        self,
        code: int,
        message: str = "",
        dxf_entity: "DXFEntity" = None,
        data: Any = None,
    ):
        self.code: int = code  # error code AuditError()
        self.entity: "DXFEntity" = dxf_entity  # source entity of error
        self.message: str = message  # error message
        self.data: Any = data  # additional data as an arbitrary object


class Auditor:
    def __init__(self, doc: Optional["Drawing"]):
        self.doc: Optional["Drawing"] = doc
        self._rootdict_handle = doc.rootdict.dxf.handle if doc else "0"
        self.errors: List[ErrorEntry] = []
        self.fixes: List[ErrorEntry] = []
        self._trashcan: Optional["EntityDB.Trashcan"] = (
            doc.entitydb.new_trashcan() if doc else None
        )
        self._post_audit_jobs = []

    def reset(self) -> None:
        self.errors = []
        self.fixes = []
        self.empty_trashcan()

    def __len__(self) -> int:
        """Returns count of unfixed errors."""
        return len(self.errors)

    def __bool__(self) -> bool:
        """Returns ``True`` if any unfixed errors exist."""
        return self.__len__() > 0

    def __iter__(self) -> Iterable[ErrorEntry]:
        """Iterate over all unfixed errors."""
        return iter(self.errors)

    @property
    def entitydb(self):
        if self.doc:
            return self.doc.entitydb
        else:
            return None

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def has_fixes(self) -> bool:
        return bool(self.fixes)

    def print_error_report(
        self, errors: List[ErrorEntry] = None, stream: TextIO = None
    ) -> None:
        def entity_str(count, code, entity):
            if entity is not None:
                return f"{count:4d}. Issue [{code}] in {str(entity)}."
            else:
                return f"{count:4d}. Issue [{code}]."

        if errors is None:
            errors = self.errors
        else:
            errors = list(errors)

        if stream is None:
            stream = sys.stdout

        if len(errors) == 0:
            stream.write("No issues found.\n\n")
        else:
            stream.write(f"{len(errors)} issues found.\n\n")
            for count, error in enumerate(errors):
                stream.write(
                    entity_str(count + 1, error.code, error.entity) + "\n"
                )
                stream.write("   " + error.message + "\n\n")

    def print_fixed_errors(self, stream: TextIO = None) -> None:
        def entity_str(count, code, entity):
            if entity is not None:
                return f"{count:4d}. Issue [{code}] fixed in {str(entity)}."
            else:
                return f"{count:4d}. Issue [{code}] fixed."

        if stream is None:
            stream = sys.stdout

        if len(self.fixes) == 0:
            stream.write("No issues fixed.\n\n")
        else:
            stream.write(f"{len(self.fixes)} issues fixed.\n\n")
            for count, error in enumerate(self.fixes):
                stream.write(
                    entity_str(count + 1, error.code, error.entity) + "\n"
                )
                stream.write("   " + error.message + "\n\n")

    def add_error(
        self,
        code: int,
        message: str = "",
        dxf_entity: "DXFEntity" = None,
        data: Any = None,
    ) -> None:
        self.errors.append(ErrorEntry(code, message, dxf_entity, data))

    def fixed_error(
        self,
        code: int,
        message: str = "",
        dxf_entity: "DXFEntity" = None,
        data: Any = None,
    ) -> None:
        self.fixes.append(ErrorEntry(code, message, dxf_entity, data))

    def purge(self, codes: Set[int]):
        """Remove error messages defined by integer error `codes`.

        This is useful to remove errors which are not important for a specific
        file usage.

        """
        self.errors = [err for err in self.errors if err.code in codes]

    def run(self) -> List[ErrorEntry]:
        # Check database integrity:
        self.doc.entitydb.audit(self)
        self.check_root_dict()
        self.check_tables()
        self.audit_all_database_entities()
        self.doc.groups.audit(self)
        self.check_block_reference_cycles()
        self.doc.layouts.audit(self)
        self.empty_trashcan()
        return self.errors

    def empty_trashcan(self):
        if self.has_trashcan:
            self._trashcan.clear()

    def trash(self, entity: "DXFEntity") -> None:
        if entity is None or not entity.is_alive:
            return
        if self.has_trashcan:
            self._trashcan.add(entity.dxf.handle)
        else:
            entity.destroy()

    @property
    def has_trashcan(self) -> bool:
        return self._trashcan is not None

    def add_post_audit_job(self, job: Callable):
        self._post_audit_jobs.append(job)

    def check_root_dict(self) -> None:
        root_dict = self.doc.rootdict
        for name in REQUIRED_ROOT_DICT_ENTRIES:
            if name not in root_dict:
                self.add_error(
                    code=AuditError.MISSING_REQUIRED_ROOT_DICT_ENTRY,
                    message=f"Missing root dict entry: {name}",
                    dxf_entity=root_dict,
                )

    def check_tables(self) -> None:
        def fix_table_head(table):
            head = table.head
            # Another exception for an invalid owner tag, but this usage is
            # covered in Auditor.check_owner_exist():
            head.dxf.owner = "0"
            handle = head.dxf.handle
            if handle is None or handle == "0":
                # Entity database does not assign new handle:
                head.dxf.handle = self.entitydb.next_handle()
                self.entitydb.add(head)
                self.fixed_error(
                    code=AuditError.INVALID_TABLE_HANDLE,
                    message=f"Fixed invalid table handle in {table.name}",
                )
            # Just to be sure owner handle is valid in every circumstance:
            table.update_owner_handles()

        table_section = self.doc.tables
        fix_table_head(table_section.viewports)
        fix_table_head(table_section.linetypes)
        fix_table_head(table_section.layers)
        fix_table_head(table_section.styles)
        fix_table_head(table_section.views)
        fix_table_head(table_section.ucs)
        fix_table_head(table_section.appids)
        fix_table_head(table_section.dimstyles)
        fix_table_head(table_section.block_records)

    def audit_all_database_entities(self) -> None:
        """Audit all entities stored in the entity database."""
        # Destruction of entities can occur while auditing.
        # Best practice to delete entities is to move them into the trashcan:
        # Auditor.trash(entity)
        db = self.doc.entitydb
        db.locked = True
        # To create new entities while auditing, add a post audit job by calling
        # Auditor.app_post_audit_job() with a callable object or
        # function as argument.
        self._post_audit_jobs = []
        for entity in db.values():
            if entity.is_alive:
                entity.audit(self)
        db.locked = False
        self.empty_trashcan()
        self.exec_post_audit_jobs()

    def exec_post_audit_jobs(self):
        for call in self._post_audit_jobs:
            call()
        self._post_audit_jobs = []

    def check_entity_linetype(self, entity: "DXFEntity") -> None:
        """Check for usage of undefined line types. AutoCAD does not load
        DXF files with undefined line types.
        """
        assert self.doc is entity.doc, "Entity from different DXF document."
        if not entity.dxf.hasattr("linetype"):
            return
        linetype = table_key(entity.dxf.linetype)
        # No table entry in linetypes required:
        if linetype in ("bylayer", "byblock"):
            return

        if linetype not in self.doc.linetypes:
            # Defaults to 'BYLAYER'
            entity.dxf.discard("linetype")
            self.fixed_error(
                code=AuditError.UNDEFINED_LINETYPE,
                message=f"Removed undefined linetype {linetype} in {str(entity)}",
                dxf_entity=entity,
                data=linetype,
            )

    def check_text_style(self, entity: "DXFEntity") -> None:
        """Check for usage of undefined text styles."""
        assert self.doc is entity.doc, "Entity from different DXF document."
        if not entity.dxf.hasattr("style"):
            return
        style = entity.dxf.style
        if style not in self.doc.styles:
            # Defaults to 'Standard'
            entity.dxf.discard("style")
            self.fixed_error(
                code=AuditError.UNDEFINED_TEXT_STYLE,
                message=f'Removed undefined text style "{style}" from {str(entity)}.',
                dxf_entity=entity,
                data=style,
            )

    def check_dimension_style(self, entity: "DXFGraphic") -> None:
        """Check for usage of undefined dimension styles."""
        assert self.doc is entity.doc, "Entity from different DXF document."
        if not entity.dxf.hasattr("dimstyle"):
            return
        dimstyle = entity.dxf.dimstyle
        if dimstyle not in self.doc.dimstyles:
            # The dimstyle attribute is not optional:
            entity.dxf.dimstyle = "Standard"
            self.fixed_error(
                code=AuditError.UNDEFINED_DIMENSION_STYLE,
                message=f'Replaced undefined dimstyle "{dimstyle}" in '
                        f'{str(entity)} by "Standard".',
                dxf_entity=entity,
                data=dimstyle,
            )

    def check_for_valid_layer_name(self, entity: "DXFEntity") -> None:
        """Check layer names for invalid characters: <>/\":;?*|='"""
        name = entity.dxf.layer
        if not validator.is_valid_layer_name(name):
            # This error can't be fixed !?
            self.add_error(
                code=AuditError.INVALID_LAYER_NAME,
                message=f'Invalid layer name "{name}" in {str(entity)}',
                dxf_entity=entity,
                data=name,
            )

    def check_entity_color_index(self, entity: "DXFGraphic") -> None:
        color = entity.dxf.color
        # 0 == BYBLOCK
        # 256 == BYLAYER
        # 257 == BYOBJECT
        if color < 0 or color > 257:
            entity.dxf.discard("color")
            self.fixed_error(
                code=AuditError.INVALID_COLOR_INDEX,
                message=f"Removed invalid color index of {str(entity)}.",
                dxf_entity=entity,
                data=color,
            )

    def check_entity_lineweight(self, entity: "DXFGraphic") -> None:
        weight = entity.dxf.lineweight
        if weight not in const.VALID_DXF_LINEWEIGHT_VALUES:
            entity.dxf.lineweight = validator.fix_lineweight(weight)
            self.fixed_error(
                code=AuditError.INVALID_LINEWEIGHT,
                message=f"Fixed invalid lineweight of {str(entity)}.",
                dxf_entity=entity,
            )

    def check_owner_exist(self, entity: "DXFEntity") -> None:
        assert self.doc is entity.doc, "Entity from different DXF document."
        if not entity.dxf.hasattr("owner"):
            return
        doc = self.doc
        owner_handle = entity.dxf.owner
        handle = entity.dxf.get("handle", "0")
        if owner_handle == "0":
            # Root-Dictionary or Table-Head:
            if handle == self._rootdict_handle or entity.dxftype() == "TABLE":
                return  # '0' handle as owner is valid
        if owner_handle not in doc.entitydb:
            if handle == self._rootdict_handle:
                entity.dxf.owner = "0"
                self.fixed_error(
                    code=AuditError.INVALID_OWNER_HANDLE,
                    message=f"Fixed invalid owner handle in root {str(self)}.",
                )
            elif entity.dxftype() == "TABLE":
                name = entity.dxf.get("name", "UNKNOWN")
                entity.dxf.owner = "0"
                self.fixed_error(
                    code=AuditError.INVALID_OWNER_HANDLE,
                    message=f"Fixed invalid owner handle for {name} table.",
                )
            else:
                self.fixed_error(
                    code=AuditError.INVALID_OWNER_HANDLE,
                    message=f"Deleted {str(entity)} entity with invalid owner "
                            f"handle #{owner_handle}.",
                )
                self.trash(doc.entitydb.get(handle))

    def check_extrusion_vector(self, entity: "DXFEntity") -> None:
        if NULLVEC.isclose(entity.dxf.extrusion):
            entity.dxf.discard("extrusion")
            self.fixed_error(
                code=AuditError.INVALID_EXTRUSION_VECTOR,
                message=f"Fixed extrusion vector for entity: {str(self)}.",
                dxf_entity=entity,
            )

    def check_block_reference_cycles(self) -> None:
        cycle_detector = BlockCycleDetector(self.doc)
        for block in self.doc.blocks:
            if cycle_detector.has_cycle(block.name):
                self.add_error(
                    code=AuditError.INVALID_BLOCK_REFERENCE_CYCLE,
                    message=f"Invalid block reference cycle detected in "
                            f'block "{block.name}".',
                    dxf_entity=block.block_record,
                )


class BlockCycleDetector:
    def __init__(self, doc: "Drawing"):
        self.key = doc.blocks.key
        self.blocks = self._build_block_ledger(doc.blocks)

    def _build_block_ledger(
        self, blocks: "BlocksSection"
    ) -> Dict[str, Set[str]]:
        ledger = dict()
        for block in blocks:
            inserts = {
                self.key(insert.dxf.name) for insert in block.query("INSERT")
            }
            ledger[self.key(block.name)] = inserts
        return ledger

    def has_cycle(self, block_name: str) -> bool:
        def check(name):
            # block 'name' does not exist: ignore this error, because it is not
            # the task of this method to detect not existing block definitions
            try:
                inserts = self.blocks[name]
            except KeyError:
                return False  # Not existing blocks can't create cycles.
            path.append(name)
            for n in inserts:
                if n in path:
                    return True
                elif check(n):
                    return True
            path.pop()
            return False

        path = []
        block_name = self.key(block_name)
        return check(block_name)


def audit(entity: "DXFEntity", doc: "Drawing") -> Auditor:
    """Setup an :class:`Auditor` object, run the audit process for `entity`
    and return result as :class:`Auditor` object.

    Args:
        entity: DXF entity to validate
        doc: bounded DXF document of `entity`

    """
    if not entity.is_alive:
        raise TypeError("Entity is destroyed.")

    # Validation of unbound entities is possible, but it is not useful
    # to validate entities against a different DXF document:
    if entity.dxf.handle is not None and not factory.is_bound(entity, doc):
        raise ValueError("Entity is bound to different DXF document.")

    auditor = Auditor(doc)
    entity.audit(auditor)
    return auditor
