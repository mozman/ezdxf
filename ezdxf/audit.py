# Purpose: audit module
# Created: 10.03.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from __future__ import unicode_literals

from ezdxf.lldxf.types import is_pointer_code
__author__ = "mozman <mozman@gmx.at>"
__all__ = ['audit']

REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')

MISSING_REQUIRED_ROOT_DICT_ENTRY = 1
UNDEFINED_LINETYPE = 2
INVALID_LAYER_NAME = 3
DUPLICATE_TABLE_ENTRY_NAME = 4
POINTER_TARGET_NOT_EXISTS = 5

INVALID_LAYER_NAME_CHARACTERS = frozenset(['<', '>', '/', '\\',  '"', ':', ';', '?', '*', '|', '=', "'"])


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


class Audit(object):
    def __init__(self, drawing):
        self.drawing = drawing
        self.errors = []

    def __len__(self):
        return len(self.errors)

    def __bool__(self):
        return self.__len__() > 0

    def __iter__(self):
        return iter(self.errors)

    def write_error_messages(self, stream):
        for error in self.errors:
            stream.write(error.message)

    def run(self):
        dxfversion = self.drawing.dxfversion
        if dxfversion > 'AC1009':  # modern style DXF13 or later
            self.check_root_dict()
        self.check_pointer_target_exists()
        self.check_table_entries()
        self.check_linetypes_exists()
        self.check_dim_styles_exists()
        self.check_for_invalid_layer_names()

    def add_error(self, code, message='', dxf_entity=None, data=None):
        error = ErrorEntry(code, message, dxf_entity, data)
        self.errors.append(error)

    def filter_errors(self, code):
        return (error for error in self.errors if error.code == code)

    def check_root_dict(self):
        root_dict = self.drawing.rootdict
        for name in REQUIRED_ROOT_DICT_ENTRIES:
            if name not in root_dict:
                self.add_error(
                    code=MISSING_REQUIRED_ROOT_DICT_ENTRY,
                    message='Missing root dict entry: {}'.format(name),
                    dxf_entity=root_dict,
                    data=name,
                )

    def check_pointer_target_exists(self):
        undefined_targets = set()
        db = self.drawing.entitydb
        for tags in db.values():
            for target_pointer in get_pointers(tags):
                if target_pointer not in db:
                    if target_pointer == '0':  # default unset pointer
                        continue
                    if target_pointer in undefined_targets:  # every undefined point just one time
                        continue
                    entity = self.drawing.get_dxf_entity(tags.get_handle())
                    self.add_error(
                        code=POINTER_TARGET_NOT_EXISTS,
                        message='Pointer target does not exist. DXF entity: {}'.format(entity.dxftype()),
                        dxf_entity=entity,
                        data=target_pointer,
                    )
                    undefined_targets.add(target_pointer)

    def check_table_entries(self):
        self.drawing.layers.audit(self)
        self.drawing.linetypes.audit(self)
        self.drawing.styles.audit(self)
        self.drawing.dimstyles.audit(self)
        self.drawing.block_records.audit(self)
        self.drawing.ucs.audit(self)
        self.drawing.appids.audit(self)
        self.drawing.views.audit(self)

    def check_linetypes_exists(self):
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        linetypes = self.drawing.linetypes

        def check_linetype_exists(name):
            if name not in linetypes:
                self.add_error(
                    code=UNDEFINED_LINETYPE,
                    message='Undefined linetype {}'.format(linetype),
                    dxf_entity=self.drawing.get_dxf_entity(handle),
                    data=linetype,
                )

        for handle, tags in self.drawing.entitydb.items():
            linetype = tags.noclass.get_first_value(6, None)  # linetype has a fixed tag value
            if linetype is not None:
                check_linetype_exists(linetype)

    def check_dim_styles_exists(self):  # TODO: implement dimension style checker
        """
        Check for usage of undefined dimension styles.
        """
        pass

    def check_for_invalid_layer_names(self):
        """
        Check layer names for invalid characters: <>/\":;?*|='
        """
        def check_layer_name_is_valid(name):
            if INVALID_LAYER_NAME_CHARACTERS.intersection(set(name)):
                self.add_error(
                    code=INVALID_LAYER_NAME,
                    message='Invalid layer name {}'.format(name),
                    dxf_entity=self.drawing.get_dxf_entity(handle),
                    data=name,
                )

        for handle, tags in self.drawing.entitydb.items():
            layer_name = tags.noclass.get_first_value(8, None)  # layer has a fixed tag value
            if layer_name is not None:
                check_layer_name_is_valid(layer_name)
