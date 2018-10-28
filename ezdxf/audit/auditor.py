# Purpose: auditor module
# Created: 10.03.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from __future__ import unicode_literals
import sys
from ezdxf.lldxf.types import is_pointer_code, DXFTag
from ezdxf.lldxf.const import Error
from ezdxf.lldxf.validator import is_valid_layer_name, is_adsk_special_layer
from ezdxf.dxfentity import DXFEntity

REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')


class ErrorEntry(object):
    def __init__(self, code, message='', dxf_entity=None, data=None):
        self.code = code
        self.entity = dxf_entity
        self.message = message
        self.data = data


def target_pointers(tags):
    for tag in tags:
        if is_pointer_code(tag.code):
            yield tag


class Auditor(object):
    def __init__(self, drawing):
        self.drawing = drawing
        self.errors = []
        self.undefined_targets = set()

    def reset(self):
        self.errors = []
        self.undefined_targets = set()

    def __len__(self):
        return len(self.errors)

    def __bool__(self):
        return self.__len__() > 0

    def __iter__(self):
        return iter(self.errors)

    def print_report(self, errors=None, stream=None):
        def entity_str(count, code, entity):
            if entity is not None:
                return "{:4d}. Issue [{}] in {} #{}".format(count, code, entity.dxftype(), entity.dxf.handle)
            else:
                return "{:4d}. Issue [{}]".format(count, code)

        if errors is None:
            errors = self.errors
        else:
            errors = list(errors)  # generator?

        if stream is None:
            stream = sys.stdout

        if len(errors) == 0:
            stream.write('No issues found.\n\n')
        else:
            stream.write('{} issues found.\n\n'.format(len(errors)))
            for count, error in enumerate(errors):
                stream.write(entity_str(count+1, error.code, error.entity) + '\n')
                stream.write('   '+error.message+'\n\n')

    @staticmethod
    def filter_zero_pointers(errors):
        for error in errors:
            if error.code == Error.POINTER_TARGET_NOT_EXISTS and error.data.value == '0':
                continue
            yield error

    def add_error(self, code, message='', dxf_entity=None, data=None):
        error = ErrorEntry(code, message, dxf_entity, data)
        self.errors.append(error)

    def run(self):
        self.reset()
        dxfversion = self.drawing.dxfversion
        if dxfversion > 'AC1009':  # modern style DXF13 or later
            self.check_root_dict()
            self.check_classes_section()
        self.check_table_entries()
        self.check_database_entities()
        return self.errors

    def check_root_dict(self):
        root_dict = self.drawing.rootdict
        for name in REQUIRED_ROOT_DICT_ENTRIES:
            if name not in root_dict:
                self.add_error(
                    code=Error.MISSING_REQUIRED_ROOT_DICT_ENTRY,
                    message='Missing root dict entry: {}'.format(name),
                    dxf_entity=root_dict,
                )

    def check_table_entries(self):
        tables = self.drawing.sections.tables

        def check_table(name):
            if name in tables:
                tables[name].audit(self)
        check_table('layers')
        check_table('linetypes')
        check_table('styles')
        check_table('dimstyles')
        check_table('ucs')
        check_table('appids')
        check_table('views')
        if self.drawing.dxfversion > 'AC1009':
            check_table('block_records')

    def check_database_entities(self):
        for handle in self.drawing.entitydb.keys():
            entity = self.drawing.get_dxf_entity(handle)
            entity.audit(self)

    def check_if_linetype_exists(self, entity):
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        if not entity.supports_dxf_attrib('linetype'):
            return
        linetype = entity.dxf.linetype
        if linetype.lower() in ('bylayer', 'byblock'):  # no table entry in linetypes required
            return

        if linetype not in self.drawing.linetypes:
            self.add_error(
                code=Error.UNDEFINED_LINETYPE,
                message='Undefined linetype: {}'.format(linetype),
                dxf_entity=entity,
            )

    def check_if_text_style_exists(self, entity):
        """
        Check for usage of undefined text styles.
        """
        if not entity.supports_dxf_attrib('style'):
            return
        style = entity.dxf.style
        if style not in self.drawing.styles:
            self.add_error(
                code=Error.UNDEFINED_TEXT_STYLE,
                message='Undefined dimstyle: {}'.format(style),
                dxf_entity=entity,
            )

    def check_if_dimension_style_exists(self, entity):
        """
        Check for usage of undefined dimension styles.
        """
        if not entity.supports_dxf_attrib('dimstyle'):
            return
        dimstyle = entity.dxf.dimstyle
        if dimstyle not in self.drawing.dimstyles:
            self.add_error(
                code=Error.UNDEFINED_DIMENSION_STYLE,
                message='Undefined dimstyle: {}'.format(dimstyle),
                dxf_entity=entity,
            )

    def check_for_valid_layer_name(self, entity):
        """
        Check layer names for invalid characters: <>/\":;?*|='
        """
        if not entity.supports_dxf_attrib('layer'):
            return
        name = entity.dxf.layer
        if not is_valid_layer_name(name):
            if self.drawing.dxfversion > 'AC1009' and is_adsk_special_layer(name):
                return
            self.add_error(
                code=Error.INVALID_LAYER_NAME,
                message='Invalid layer name: {}'.format(name),
                dxf_entity=entity,
            )

    def check_for_valid_color_index(self, entity):
        if not entity.supports_dxf_attrib('color'):
            return
        color = entity.dxf.color
        # 0 == BYBLOCK
        # 256 == BYLAYER
        # 257 == BYOBJECT
        if color < 0 or color > 257:
            self.add_error(
                code=Error.INVALID_COLOR_INDEX,
                message='Invalid color index: {}'.format(color),
                dxf_entity=entity,
            )

    def check_for_existing_owner(self, entity):
        if not entity.supports_dxf_attrib('owner'):
            return
        owner_handle = entity.dxf.owner
        if owner_handle not in self.drawing.entitydb:
            self.add_error(
                code=Error.INVALID_OWNER_HANDLE,
                message='Invalid owner handle: #{}'.format(owner_handle),
                dxf_entity=entity,
            )

    def check_pointer_target_exists(self, entity, zero_pointer_valid=False, ignore_codes=None):
        assert isinstance(entity, DXFEntity)
        if ignore_codes is None:
            ignore_codes = set()
        else:
            ignore_codes = set(ignore_codes)

        db = self.drawing.entitydb
        for tag in target_pointers(entity.tags):
            group_code, handle = tag
            if group_code in ignore_codes:
                continue
            if handle not in db:
                if handle == '0' and zero_pointer_valid:  # default unset pointer
                    continue
                if handle in self.undefined_targets:  # for every undefined pointer add just one error message
                    continue
                self.add_error(
                    code=Error.POINTER_TARGET_NOT_EXISTS,
                    message='Pointer target does not exist: ({}, #{})'.format(group_code, handle),
                    dxf_entity=entity,
                    data=tag,
                )
                self.undefined_targets.add(handle)

    def check_handles_exists(self, entity, handles, zero_pointer_valid=False):
        db = self.drawing.entitydb
        for handle in handles:
            if handle not in db:
                if handle == '0' and zero_pointer_valid:  # default unset pointer
                    continue
                if handle in self.undefined_targets:  # for every undefined pointer add just one error message
                    continue
                self.add_error(
                    code=Error.POINTER_TARGET_NOT_EXISTS,
                    message='handle target does not exist: (#{})'.format(handle),
                    dxf_entity=entity,
                    data=DXFTag(-1, handle),  # DXFTag is expected
                )
                self.undefined_targets.add(handle)

    def check_classes_section(self):
        def check_invalid_group_codes(valid_codes):
            def find_invalid_group_code(tags):
                for code, value in tags.noclass:
                    if code not in valid_codes:
                        return code
                return None

            for cls in self.drawing.sections.classes:
                invalid_code = find_invalid_group_code(cls.tags)
                if invalid_code is not None:
                    self.add_error(
                        code=Error.INVALID_GROUP_CODE_IN_CLASS_DEFINITION,
                        message='Invalid group code {} in CLASS definition: {}.'.format(invalid_code, cls.dxf.name),
                    )

        dxfversion = self.drawing.dxfversion
        if dxfversion <= 'AC1009':
            return
        if dxfversion < 'AC1018':
            check_invalid_group_codes(valid_codes={0, 1, 2, 3, 90, 280, 281})
        else:
            check_invalid_group_codes(valid_codes={0, 1, 2, 3, 90, 91, 280, 281})
