# Purpose: audit module
# Created: 10.03.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
"""
audit(drawing, stream): check a DXF drawing for errors.
"""
from __future__ import unicode_literals
import sys
__author__ = "mozman <mozman@gmx.at>"
__all__ = ['audit']

REQUIRED_ROOT_DICT_ENTRIES = ('ACAD_GROUP', 'ACAD_PLOTSTYLENAME')


def audit(drawing, stream=None):
    if stream is None:
        stream = sys.stdout
    auditor = Audit(drawing, stream)
    auditor.run()


class Audit(object):
    def __init__(self, drawing, stream):
        self.drawing = drawing
        self.writer = stream

    @property
    def entitydb(self):
        return self.drawing.entitydb

    def all_drawing_entities(self):
        for handle in self.entitydb.keys():
            yield self.drawing.get_dxf_entity(handle)

    def write(self, message):
        self.writer.write(message)

    def run(self):
        dxfversion = self.drawing.dxfversion
        release = self.drawing.acad_release
        self.write('Start audit for DXF version {} release {}\n'.format(dxfversion, release))
        if dxfversion > 'AC1009':  # modern style DXF13 or later
            self.check_root_dict()
        self.check_linetypes()

    def check_root_dict(self):
        error_count = 0
        self.write('Checking root dict: ')
        root_dict = self.drawing.rootdict
        for name in REQUIRED_ROOT_DICT_ENTRIES:
            if name not in root_dict:
                self.write('\n  missing entry: {}'.format(name))
                error_count += 1
        if error_count == 0:
            self.write('ok\n')
        else:
            self.write('\n  {} errors found\n'.format(error_count))

    def check_linetypes(self):
        """
        Check for usage of undefined line types. AutoCAD does not load DXF files with undefined line types.
        """
        self.write('Checking line types: ')
        errors = self.check_used_linetypes()
        if len(errors):
            self.write('{} errors found\n'.format(len(errors)))
            for msg in errors:
                self.write(msg)
        else:
            self.write('ok\n')

    def check_used_linetypes(self):
        linetypes = self.drawing.linetypes
        attrib = 'linetype'
        error_messages = []
        # examine entities in the ENTITIES section
        # and all block layouts
        layouts = [self.drawing.entities]
        layouts.extend(self.drawing.blocks)
        for layout in layouts:
            for entity in layout:
                if not entity.supports_dxf_attrib(attrib):
                    continue
                linetype = entity.get_dxf_attrib(attrib, default=None)
                if linetype is not None:
                    if linetype not in linetypes:
                        dxftype = entity.dxftype()
                        handle = entity.dxf.handle
                        msg = '  undefined linetype {} in entity: {} handle={}\n'.format(linetype, dxftype, handle)
                        error_messages.append(msg)
        return error_messages
