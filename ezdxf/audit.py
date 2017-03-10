# Purpose: audit module
# Created: 10.03.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"
__all__ = ['audit']

REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')

MISSING_REQUIRED_ROOT_DICT_ENTRY = 1
UNDEFINED_LINETYPE = 2


class ErrorEntry(object):
    def __init__(self, code, message='', dxf_entity=None, data=None):
        self.code = code
        self.dxf_entity = dxf_entity
        self.message = message
        self.data = data


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
        self.check_linetypes()

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

    def check_linetypes(self):
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        linetypes = self.drawing.linetypes
        attrib = 'linetype'
        # examine entities in the ENTITIES section
        # and all block layouts
        layouts = [self.drawing.entities]
        layouts.extend(self.drawing.blocks)
        for layout in layouts:
            for entity in layout:
                if not entity.supports_dxf_attrib(attrib):
                    continue
                linetype = entity.get_dxf_attrib(attrib, default=None)
                if linetype is None:
                    continue
                if linetype not in linetypes:
                    self.add_error(
                        code=UNDEFINED_LINETYPE,
                        message='Undefined linetype {}'.format(linetype),
                        dxf_entity=entity,
                        data=linetype,
                    )

