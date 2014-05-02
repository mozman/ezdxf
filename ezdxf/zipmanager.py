# Purpose: read DXF files from zip archive
# Created: 02.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

__author__ = "mozman <mozman@gmx.at>"

import sys
import zipfile
from contextlib import contextmanager

from .c23 import ustr
from.tags import dxf_info


class ZipReader(object):
    def __init__(self, zip_archive_name, dxf_file_name=None):
        if not zipfile.is_zipfile(zip_archive_name):
            raise IOError("'{}' is not a zip archive.".format(zip_archive_name))
        self.zip_achive_name = zip_archive_name
        self.zip_archive = None
        self.dxf_file_name = dxf_file_name
        self.dxf_file = None
        self.encoding = 'cp1252'

    def open(self):
        def open_dxf_file():
            return self.zip_archive.open(self.dxf_file_name, mode='rU')

        self.zip_archive = zipfile.ZipFile(self.zip_achive_name)
        if self.dxf_file_name is None:
            self.dxf_file_name = self.get_first_dxf_filename()
        self.dxf_file = open_dxf_file()
        if not self.is_dxf_file():
            raise IOError("'{}' is not a DXF file.".format(self.dxf_file_name))
        self.dxf_file = open_dxf_file()  # restart
        self.get_dxf_encoding()
        self.dxf_file = open_dxf_file()  # restart

    def get_first_dxf_filename(self):
        for name in self.zip_archive.namelist():
            if name.lower().endswith('.dxf'):
                return name
        raise IOError("'{}' has no DXF files.")

    def is_dxf_file(self):
        # TODO: check for DXF file
        return True

    def get_dxf_encoding(self):
        info = dxf_info(self)
        self.encoding = info.encoding

    def readline(self):
        next_line = self.dxf_file.readline()
        return ustr(next_line, self.encoding)

    def close(self):
        self.zip_archive.close()


@contextmanager
def ctxZipReader(zip_achive, filename=None):
    zip_reader = ZipReader(zip_achive, filename)
    zip_reader.open()
    yield zip_reader
    zip_reader.close()