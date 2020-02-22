# Purpose: auditor module
# Created: 10.03.2017
# Copyright (c) 2017-2020, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from enum import IntEnum
from typing import TYPE_CHECKING, Iterable, List, Set, TextIO, Any

import sys
from ezdxf.lldxf.types import is_pointer_code, DXFTag
from ezdxf.lldxf.validator import is_valid_layer_name, is_adsk_special_layer
from ezdxf.entities.dxfentity import DXFEntity

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, Drawing, DXFGraphic


class AuditError(IntEnum):
    MISSING_REQUIRED_ROOT_DICT_ENTRY = 1
    DUPLICATE_TABLE_ENTRY_NAME = 2
    POINTER_TARGET_NOT_EXISTS = 3
    TABLE_NOT_FOUND = 4
    UNDEFINED_LINETYPE = 100
    UNDEFINED_DIMENSION_STYLE = 101
    UNDEFINED_TEXT_STYLE = 102
    INVALID_LAYER_NAME = 200
    INVALID_COLOR_INDEX = 201
    INVALID_OWNER_HANDLE = 202
    INVALID_DICTIONARY_ENTRY = 203
    INVALID_ENTITY_HANDLE = 204


REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')


class ErrorEntry:
    def __init__(self, code: int, message: str = '', dxf_entity: 'DXFEntity' = None, data: Any = None):
        self.code = code  # error code AuditError()
        self.entity = dxf_entity  # source entity of error
        self.message = message  # error message
        self.data = data  # additional data as an arbitrary object


def target_pointers(tags: Iterable[DXFTag]) -> Iterable[DXFTag]:
    for tag in tags:
        if is_pointer_code(tag.code):
            yield tag


class Auditor:
    def __init__(self, doc: 'Drawing'):
        self.doc = doc
        self.errors = []  # type: List[ErrorEntry]
        self.fixes = []  # type: List[ErrorEntry]
        self.undefined_targets = set()  # type: Set[str]

    def reset(self) -> None:
        self.errors = []
        self.fixes = []
        self.undefined_targets = set()

    def __len__(self) -> int:
        """ Returns count of unfixed errors. """
        return len(self.errors)

    def __bool__(self) -> bool:
        """ Returns ``True`` if any unfixed errors exist. """
        return self.__len__() > 0

    def __iter__(self) -> Iterable[ErrorEntry]:
        """ Iterate over all unfixed errors. """
        return iter(self.errors)

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

    @staticmethod
    def filter_zero_pointers(errors: Iterable[ErrorEntry]) -> Iterable[ErrorEntry]:
        for error in errors:
            if error.code == AuditError.POINTER_TARGET_NOT_EXISTS and error.data == '0':
                continue
            yield error

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
        return self.errors

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
        for entity in self.doc.entitydb.values():
            entity.audit(self)

    def check_entity_linetype(self, entity: 'DXFEntity') -> None:
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('linetype'):
            return
        linetype = entity.dxf.linetype
        if linetype.lower() in ('bylayer', 'byblock'):  # no table entry in linetypes required
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
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('layer'):
            return
        name = entity.dxf.layer
        if not is_valid_layer_name(name):
            if self.doc.dxfversion > 'AC1009' and is_adsk_special_layer(name):
                return
            # This error can't be fixed !?
            self.add_error(
                code=AuditError.INVALID_LAYER_NAME,
                message=f'Invalid layer name "{name}" in {str(entity)}',
                dxf_entity=entity,
                data=name,
            )

    def check_entity_color_index(self, entity: 'DXFGraphic') -> None:
        if not entity.dxf.hasattr('color'):
            return
        # Do not use for LAYER entity
        color = entity.dxf.color
        # 0 == BYBLOCK
        # 256 == BYLAYER
        # 257 == BYOBJECT
        if color < 0 or color > 257:
            entity.dxf.discard('color')
            self.fixed_error(
                code=AuditError.INVALID_COLOR_INDEX,
                message=f'Removed invalid color index from {str(entity)}.',
                dxf_entity=entity,
                data=color,
            )

    def check_owner_exist(self, entity: 'DXFEntity') -> None:
        # tables - owner of table entries - are not stored in the entitydb
        assert self.doc is entity.doc, 'Entity from different DXF document.'
        if not entity.dxf.hasattr('owner'):
            return
        owner_handle = entity.dxf.owner
        if owner_handle not in self.doc.entitydb:
            # this error can't be fixed here
            self.add_error(
                code=AuditError.INVALID_OWNER_HANDLE,
                message=f'Invalid owner handle #{owner_handle} in {str(entity)}.',
                dxf_entity=entity,
                data=owner_handle,
            )
