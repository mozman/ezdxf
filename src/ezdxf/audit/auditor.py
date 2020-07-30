# Purpose: auditor module
# Created: 10.03.2017
# Copyright (c) 2017-2020, Manfred Moitzi
# License: MIT License
from enum import IntEnum
from typing import TYPE_CHECKING, Iterable, List, Set, TextIO, Any, Dict

import sys
from ezdxf.lldxf.validator import is_valid_layer_name, fix_lineweight
from ezdxf.lldxf.const import VALID_DXF_LINEWEIGHT_VALUES
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.math import NULLVEC
from ezdxf.sections.table import table_key

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, Drawing, DXFGraphic, BlocksSection

__all__ = ['Auditor', 'AuditError', 'is_healthy']


class AuditError(IntEnum):
    # DXF structure errors:
    MISSING_REQUIRED_ROOT_DICT_ENTRY = 1
    DUPLICATE_TABLE_ENTRY_NAME = 2
    POINTER_TARGET_NOT_EXIST = 3
    TABLE_NOT_FOUND = 4
    UNDEFINED_LINETYPE = 100
    UNDEFINED_DIMENSION_STYLE = 101
    UNDEFINED_TEXT_STYLE = 102
    UNDEFINED_BLOCK = 103
    INVALID_BLOCK_REFERENCE_CYCLE = 104
    REMOVE_EMPTY_GROUP = 105
    GROUP_ENTITIES_IN_DIFFERENT_LAYOUTS = 106
    MISSING_REQUIRED_SEQEND = 107

    # DXF entity property errors:
    INVALID_ENTITY_HANDLE = 201
    INVALID_OWNER_HANDLE = 202
    INVALID_LAYER_NAME = 203
    INVALID_COLOR_INDEX = 204
    INVALID_LINEWEIGHT = 205

    # DXF entity geometry or content errors:
    INVALID_EXTRUSION_VECTOR = 210
    INVALID_MAJOR_AXIS = 211
    INVALID_VERTEX_COUNT = 212
    INVALID_DICTIONARY_ENTRY = 213
    INVALID_CHARACTER = 214


REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')


class ErrorEntry:
    def __init__(self, code: int, message: str = '', dxf_entity: 'DXFEntity' = None, data: Any = None):
        self.code = code  # error code AuditError()
        self.entity = dxf_entity  # source entity of error
        self.message = message  # error message
        self.data = data  # additional data as an arbitrary object


class Auditor:
    def __init__(self, doc: 'Drawing'):
        self.doc = doc
        self._rootdict_handle = doc.rootdict.dxf.handle if doc else '0'
        self.errors: List[ErrorEntry] = []
        self.fixes: List[ErrorEntry] = []

    def reset(self) -> None:
        self.errors = []
        self.fixes = []

    def __len__(self) -> int:
        """ Returns count of unfixed errors. """
        return len(self.errors)

    def __bool__(self) -> bool:
        """ Returns ``True`` if any unfixed errors exist. """
        return self.__len__() > 0

    def __iter__(self) -> Iterable[ErrorEntry]:
        """ Iterate over all unfixed errors. """
        return iter(self.errors)

    @property
    def entitydb(self):
        if self.doc:
            return self.doc.entitydb
        else:
            return None

    def print_error_report(self, errors: List[ErrorEntry] = None, stream: TextIO = None) -> None:
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
            stream.write('No issues found.\n\n')
        else:
            stream.write(f'{len(errors)} issues found.\n\n')
            for count, error in enumerate(errors):
                stream.write(entity_str(count + 1, error.code, error.entity) + '\n')
                stream.write('   ' + error.message + '\n\n')

    def print_fixed_errors(self, stream: TextIO = None) -> None:
        def entity_str(count, code, entity):
            if entity is not None:
                return f"{count:4d}. Issue [{code}] fixed in {str(entity)}."
            else:
                return f"{count:4d}. Issue [{code}] fixed."

        if stream is None:
            stream = sys.stdout

        if len(self.fixes) == 0:
            stream.write('No issues fixed.\n\n')
        else:
            stream.write(f'{len(self.fixes)} issues fixed.\n\n')
            for count, error in enumerate(self.fixes):
                stream.write(entity_str(count + 1, error.code, error.entity) + '\n')
                stream.write('   ' + error.message + '\n\n')

    def add_error(self, code: int, message: str = '', dxf_entity: 'DXFEntity' = None, data: Any = None) -> None:
        self.errors.append(ErrorEntry(code, message, dxf_entity, data))

    def fixed_error(self, code: int, message: str = '', dxf_entity: 'DXFEntity' = None, data: Any = None) -> None:
        self.fixes.append(ErrorEntry(code, message, dxf_entity, data))

    def run(self) -> List[ErrorEntry]:
        self.reset()
        self.doc.entitydb.audit(self)
        self.check_root_dict()
        self.check_table_structures()
        self.check_database_entities()
        self.doc.groups.audit(self)
        self.check_block_reference_cycles()
        self.empty_trashcan()
        return self.errors

    def empty_trashcan(self):
        if self.has_trashcan:
            self.entitydb.empty_trashcan()

    def trash(self, handle: str) -> None:
        if self.has_trashcan:
            self.entitydb.trash(handle)

    @property
    def has_trashcan(self) -> bool:
        return self.entitydb is not None

    def check_root_dict(self) -> None:
        root_dict = self.doc.rootdict
        for name in REQUIRED_ROOT_DICT_ENTRIES:
            if name not in root_dict:
                self.add_error(
                    code=AuditError.MISSING_REQUIRED_ROOT_DICT_ENTRY,
                    message=f'Missing root dict entry: {name}',
                    dxf_entity=root_dict,
                )

    def check_table_structures(self) -> None:
        """ Check table structures. """
        # Tables or more precise the 'table head' is not stored in the entity database
        # Table entries are checked as database entities
        tables = self.doc.tables
        tables.linetypes.audit(self)
        tables.layers.audit(self)
        tables.styles.audit(self)
        tables.dimstyles.audit(self)
        tables.ucs.audit(self)
        tables.appids.audit(self)
        tables.views.audit(self)
        tables.block_records.audit(self)

    def check_database_entities(self) -> None:
        """ Check all entities stored in the entity database. """
        # deleting of entities can occur, while auditing
        db = self.doc.entitydb
        db.locked = True
        for entity in db.values():
            if entity.is_alive:
                entity.audit(self)
        db.locked = False
        db.empty_trashcan()

    def check_entity_linetype(self, entity: 'DXFEntity') -> None:
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('linetype'):
            return
        linetype = table_key(entity.dxf.linetype)
        if linetype in ('bylayer', 'byblock'):  # no table entry in linetypes required
            return

        if linetype not in self.doc.linetypes:
            # linetype is optional so discarding resets to 'BYLAYER'
            entity.dxf.discard('linetype')
            self.fixed_error(
                code=AuditError.UNDEFINED_LINETYPE,
                message=f'Removed undefined linetype {linetype} in {str(entity)}',
                dxf_entity=entity,
                data=linetype,
            )

    def check_text_style(self, entity: 'DXFEntity') -> None:
        """
        Check for usage of undefined text styles.
        """
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('style'):
            return
        style = entity.dxf.style
        if style not in self.doc.styles:
            # text style is optional in TEXT and MTEXT
            entity.dxf.discard('style')
            self.fixed_error(
                code=AuditError.UNDEFINED_TEXT_STYLE,
                message=f'Removed undefined text style "{style}" from {str(entity)}.',
                dxf_entity=entity,
                data=style,
            )

    def check_dimension_style(self, entity: 'DXFGraphic') -> None:
        """
        Check for usage of undefined dimension styles.
        """
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('dimstyle'):
            return
        dimstyle = entity.dxf.dimstyle
        if dimstyle not in self.doc.dimstyles:
            # dimstyle attribute is not optional
            entity.dxf.dimstyle = 'Standard'
            self.fixed_error(
                code=AuditError.UNDEFINED_DIMENSION_STYLE,
                message=f'Replaced undefined dimstyle "{dimstyle}" in {str(entity)} by "Standard".',
                dxf_entity=entity,
                data=dimstyle,
            )

    def check_for_valid_layer_name(self, entity: 'DXFEntity') -> None:
        """
        Check layer names for invalid characters: <>/\":;?*|='
        """
        name = entity.dxf.layer
        if not is_valid_layer_name(name):
            # This error can't be fixed !?
            self.add_error(
                code=AuditError.INVALID_LAYER_NAME,
                message=f'Invalid layer name "{name}" in {str(entity)}',
                dxf_entity=entity,
                data=name,
            )

    def check_entity_color_index(self, entity: 'DXFGraphic') -> None:
        color = entity.dxf.color
        # 0 == BYBLOCK
        # 256 == BYLAYER
        # 257 == BYOBJECT
        if color < 0 or color > 257:
            entity.dxf.discard('color')
            self.fixed_error(
                code=AuditError.INVALID_COLOR_INDEX,
                message=f'Removed invalid color index of {str(entity)}.',
                dxf_entity=entity,
                data=color,
            )

    def check_entity_lineweight(self, entity: 'DXFGraphic') -> None:
        weight = entity.dxf.lineweight
        if weight not in VALID_DXF_LINEWEIGHT_VALUES:
            entity.dxf.lineweight = fix_lineweight(weight)
            self.fixed_error(
                code=AuditError.INVALID_LINEWEIGHT,
                message=f'Fixed invalid lineweight of {str(entity)}.',
                dxf_entity=entity,
            )

    def check_owner_exist(self, entity: 'DXFEntity') -> None:
        # tables - owner of table entries - are not stored in the entitydb
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('owner'):
            return
        doc = self.doc
        owner_handle = entity.dxf.owner
        handle = entity.dxf.get('handle', '0')
        if owner_handle == '0':
            if handle == self._rootdict_handle:
                return  # valid '0' handle as owner

        if owner_handle not in doc.entitydb:
            if handle == self._rootdict_handle:
                entity.dxf.owner = '0'
                self.fixed_error(
                    code=AuditError.INVALID_OWNER_HANDLE,
                    message=f'Fixed invalid owner handle in root {str(self)}.',
                )
            else:
                self.fixed_error(
                    code=AuditError.INVALID_OWNER_HANDLE,
                    message=f'Deleted {str(entity)} entity without valid owner handle #{owner_handle}.',
                )
                self.trash(handle)

    def check_extrusion_vector(self, entity: 'DXFEntity') -> None:
        if NULLVEC.isclose(entity.dxf.extrusion):
            entity.dxf.discard('extrusion')
            self.fixed_error(
                code=AuditError.INVALID_EXTRUSION_VECTOR,
                message=f'Fixed extrusion vector for entity: {str(self)}.',
                dxf_entity=entity,
            )

    def check_block_reference_cycles(self) -> None:
        cycle_detector = BlockCycleDetector(self.doc)
        for block in self.doc.blocks:
            if cycle_detector.has_cycle(block.name):
                self.add_error(
                    code=AuditError.INVALID_BLOCK_REFERENCE_CYCLE,
                    message=f'Invalid block reference cycle detected in block "{block.name}".',
                    dxf_entity=block.block_record,
                )


class BlockCycleDetector:
    def __init__(self, doc: 'Drawing'):
        self.key = doc.blocks.key
        self.blocks = self._build_block_ledger(doc.blocks)

    def _build_block_ledger(self, blocks: 'BlocksSection') -> Dict[str, Set[str]]:
        ledger = dict()
        for block in blocks:
            inserts = {self.key(insert.dxf.name) for insert in block.query('INSERT')}
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


def is_healthy(entity: 'DXFEntity') -> bool:
    """
    Returns ``True`` if any error exist or any fixes has been applied.

    A returned ``True`` should show a valid entity state according to
    the DXF reference as far `ezdxf` can check this state.
    
    Intended usage: testing if an DXF entity is in good shape.

    (internal API)
    """
    auditor = Auditor(entity.doc)
    entity.audit(auditor)
    return len(auditor.errors) > 0 or len(auditor.fixes) > 0
