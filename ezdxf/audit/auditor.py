# Purpose: auditor module
# Created: 10.03.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from typing import TYPE_CHECKING, Iterable, List, Set, TextIO, Any

import sys
from ezdxf.lldxf.types import is_pointer_code, DXFTag
from ezdxf.lldxf.const import Error
from ezdxf.lldxf.validator import is_valid_layer_name, is_adsk_special_layer
from ezdxf.entities.dxfentity import DXFEntity

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, Drawing

REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')


class ErrorEntry:
    def __init__(self, code: int, message: str = '', dxf_entity: 'DXFEntity' = None, data: Any = None):
        self.code = code
        self.entity = dxf_entity
        self.message = message
        self.data = data


def target_pointers(tags: Iterable[DXFTag]) -> Iterable[DXFTag]:
    for tag in tags:
        if is_pointer_code(tag.code):
            yield tag


class Auditor:
    def __init__(self, doc: 'Drawing'):
        self.doc = doc
        self.errors = []  # type: List[ErrorEntry]
        self.undefined_targets = set()  # type: Set[str]

    def reset(self) -> None:
        self.errors = []
        self.undefined_targets = set()

    def __len__(self) -> int:
        return len(self.errors)

    def __bool__(self) -> bool:
        return self.__len__() > 0

    def __iter__(self) -> Iterable[ErrorEntry]:
        return iter(self.errors)

    def print_report(self, errors: List[ErrorEntry] = None, stream: TextIO = None) -> None:
        def entity_str(count, code, entity):
            if entity is not None:
                handle = entity.dxf.handle
                type_ = entity.dxftype()
                return f"{count:4d}. Issue [{code}] in {type_} #{handle}"
            else:
                return f"{count:4d}. Issue [{code}]"

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

    @staticmethod
    def filter_zero_pointers(errors: Iterable[ErrorEntry]) -> Iterable[ErrorEntry]:
        for error in errors:
            if error.code == Error.POINTER_TARGET_NOT_EXISTS and error.data == '0':
                continue
            yield error

    def add_error(self, code: int, message: str = '', dxf_entity: 'DXFEntity' = None, data: Any = None) -> None:
        error = ErrorEntry(code, message, dxf_entity, data)
        self.errors.append(error)

    def run(self) -> List[ErrorEntry]:
        self.reset()
        dxfversion = self.doc.dxfversion
        if dxfversion > 'AC1009':  # modern style DXF13 or later
            self.check_root_dict()
        self.check_table_entries()
        self.check_database_entities()
        return self.errors

    def check_root_dict(self) -> None:
        root_dict = self.doc.rootdict
        for name in REQUIRED_ROOT_DICT_ENTRIES:
            if name not in root_dict:
                self.add_error(
                    code=Error.MISSING_REQUIRED_ROOT_DICT_ENTRY,
                    message=f'Missing root dict entry: {name}',
                    dxf_entity=root_dict,
                )

    def check_table_entries(self) -> None:
        tables = self.doc.tables
        tables.layers.audit(self)
        tables.linetypes.audit(self)
        tables.styles.audit(self)
        tables.dimstyles.audit(self)
        tables.ucs.audit(self)
        tables.appids.audit(self)
        tables.views.audit(self)
        tables.block_records.audit(self)

    def check_database_entities(self) -> None:
        for entity in self.doc.entitydb.values():
            entity.audit(self)

    def check_if_linetype_exists(self, entity: 'DXFEntity') -> None:
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        if not entity.is_supported_dxf_attrib('linetype'):
            return
        linetype = entity.dxf.linetype
        if linetype.lower() in ('bylayer', 'byblock'):  # no table entry in linetypes required
            return

        if linetype not in self.doc.linetypes:
            self.add_error(
                code=Error.UNDEFINED_LINETYPE,
                message=f'Undefined linetype: {linetype}',
                dxf_entity=entity,
            )

    def check_if_text_style_exists(self, entity: 'DXFEntity') -> None:
        """
        Check for usage of undefined text styles.
        """
        if not entity.is_supported_dxf_attrib('style'):
            return
        style = entity.dxf.style
        if style not in self.doc.styles:
            self.add_error(
                code=Error.UNDEFINED_TEXT_STYLE,
                message=f'Undefined text style: {style}',
                dxf_entity=entity,
            )

    def check_if_dimension_style_exists(self, entity: 'DXFEntity') -> None:
        """
        Check for usage of undefined dimension styles.
        """
        if not entity.is_supported_dxf_attrib('dimstyle'):
            return
        dimstyle = entity.dxf.dimstyle
        if dimstyle not in self.doc.dimstyles:
            self.add_error(
                code=Error.UNDEFINED_DIMENSION_STYLE,
                message=f'Undefined dimstyle: {dimstyle}',
                dxf_entity=entity,
            )

    def check_for_valid_layer_name(self, entity: 'DXFEntity') -> None:
        """
        Check layer names for invalid characters: <>/\":;?*|='
        """
        if not entity.is_supported_dxf_attrib('layer'):
            return
        name = entity.dxf.layer
        if not is_valid_layer_name(name):
            if self.doc.dxfversion > 'AC1009' and is_adsk_special_layer(name):
                return
            self.add_error(
                code=Error.INVALID_LAYER_NAME,
                message=f'Invalid layer name: {name}',
                dxf_entity=entity,
            )

    def check_for_valid_color_index(self, entity: 'DXFEntity') -> None:
        # check if exist, because getting none existing attributes doesn't rise an exception instead returns the
        # default value.
        if not entity.dxf.hasattr('color'):
            return
        color = entity.dxf.color
        # 0 == BYBLOCK
        # 256 == BYLAYER
        # 257 == BYOBJECT
        if color < 0 or color > 257:
            self.add_error(
                code=Error.INVALID_COLOR_INDEX,
                message=f'Invalid color index: {color}',
                dxf_entity=entity,
            )

    def check_owner_exist(self, entity: 'DXFEntity') -> None:
        if not entity.dxf.hasattr('owner'):
            return
        owner_handle = entity.dxf.owner
        if owner_handle not in self.doc.entitydb:
            self.add_error(
                code=Error.INVALID_OWNER_HANDLE,
                message=f'Invalid owner handle: #{owner_handle}',
                dxf_entity=entity,
            )

    def check_pointer_target_exist(self, entity: 'DXFEntity', zero_pointer_valid: bool = False) -> None:
        assert isinstance(entity, DXFEntity)
        self.check_handles_exist(entity, entity.check_pointers(), zero_pointer_valid)

    def check_handles_exist(self, entity: 'DXFEntity',
                            handles: Iterable[str],
                            zero_pointer_valid: bool = False) -> None:
        db = self.doc.entitydb
        for handle in handles:
            if handle not in db:
                if handle == '0' and zero_pointer_valid:  # default unset pointer
                    continue
                if handle in self.undefined_targets:  # for every undefined pointer add just one error message
                    continue
                self.add_error(
                    code=Error.POINTER_TARGET_NOT_EXISTS,
                    message=f'Handle target does not exist: (#{handle})',
                    dxf_entity=entity,
                    data=handle,
                )
                self.undefined_targets.add(handle)
