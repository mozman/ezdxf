# Purpose: audit module
# Created: 10.03.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from __future__ import unicode_literals
from ezdxf.lldxf.types import is_pointer_code
from ezdxf.lldxf.const import Error
from ezdxf.lldxf.validator import is_valid_layer_name
from ezdxf.dxfentity import DXFEntity

REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')


class ErrorEntry(object):
    def __init__(self, code, message='', dxf_entity=None, data=None):
        self.code = code
        self.dxf_entity = dxf_entity
        self.message = message
        self.data = data


def get_pointers(tags):
    for tag in tags:
        if is_pointer_code(tag.code):
            yield tag.value


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

    def write_error_messages(self, stream):
        for error in self.errors:
            stream.write(error.message)

    def add_error(self, code, message='', dxf_entity=None, data=None):
        error = ErrorEntry(code, message, dxf_entity, data)
        self.errors.append(error)

    def filter_errors(self, code):
        return (error for error in self.errors if error.code == code)

    def run(self):
        self.reset()
        dxfversion = self.drawing.dxfversion
        if dxfversion > 'AC1009':  # modern style DXF13 or later
            self.check_root_dict()
        self.check_table_entries()
        self.check_database_entities()

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
        self.drawing.layers.audit(self)
        self.drawing.linetypes.audit(self)
        self.drawing.styles.audit(self)
        self.drawing.dimstyles.audit(self)
        self.drawing.block_records.audit(self)
        self.drawing.ucs.audit(self)
        self.drawing.appids.audit(self)
        self.drawing.views.audit(self)

    def check_database_entities(self):
        for handle in self.drawing.entitydb.keys():
            entity = self.drawing.get_dxf_entity(handle)
            entity.audit(self)

    def check_if_linetype_exists(self, entity):
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        linetype = entity.dxf.linetype
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
        name = entity.dxf.layer
        if not is_valid_layer_name(name):
            self.add_error(
                code=Error.INVALID_LAYER_NAME,
                message='Invalid layer name: {}'.format(name),
                dxf_entity=entity,
            )

    def check_for_valid_color_index(self, entity):
        color = entity.dxf.color
        if color < 0 or color > 256:
            self.add_error(
                code=Error.INVALID_COLOR_INDEX,
                message='Invalid color index: {}'.format(color),
                dxf_entity=entity,
            )

    def check_for_existing_owner(self, entity):
        owner_handle = entity.dxf.owner
        if owner_handle not in self.drawing.entitydb:
            self.add_error(
                code=Error.INVALID_OWNER_HANDLE,
                message='Invalid owner handle: #{}'.format(owner_handle),
                dxf_entity=entity,
            )

    def check_pointer_target_exists(self, entity, invalid_zero=False):
        assert isinstance(entity, DXFEntity)
        db = self.drawing.entitydb
        for target_pointer in get_pointers(entity.tags):
            if target_pointer not in db:
                if target_pointer == '0' and not invalid_zero:  # default unset pointer
                    continue
                if target_pointer in self.undefined_targets:  # every undefined point just one time
                    continue
                self.add_error(
                    code=Error.POINTER_TARGET_NOT_EXISTS,
                    message='Pointer target does not exist: #{}'.format(target_pointer),
                    dxf_entity=entity,
                )
                self.undefined_targets.add(target_pointer)
