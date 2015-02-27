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
from .tags import dxf_info

if sys.version_info[:2] < (3, 4):
    ZIP_OPEN_FILE_MODE = 'rU'
    HACK_ZIP_EXT_FILE = False
else:
    ZIP_OPEN_FILE_MODE = 'r'
    HACK_ZIP_EXT_FILE = True  # if sys.version_info[:3] <= (3, 4, 0) else False  # if later versions fix this problem


class ZipReader(object):
    def __init__(self, zip_archive_name):
        if not zipfile.is_zipfile(zip_archive_name):
            raise IOError("'{}' is not a zip archive.".format(zip_archive_name))
        self.zip_archive_name = zip_archive_name
        self.zip_archive = None
        self.dxf_file_name = None
        self.dxf_file = None
        self.encoding = 'cp1252'

    def open(self, dxf_file_name=None):
        def open_dxf_file():
            zip_ext_file = self.zip_archive.open(self.dxf_file_name, mode=ZIP_OPEN_FILE_MODE)
            if HACK_ZIP_EXT_FILE:
                # 'U' in mode deprecated, but ZipExtFile._universal is only set if 'U' is in mode ...
                zip_ext_file._universal = True
            return zip_ext_file

        self.zip_archive = zipfile.ZipFile(self.zip_archive_name)
        self.dxf_file_name = dxf_file_name if dxf_file_name is not None else self.get_first_dxf_file_name()
        self.dxf_file = open_dxf_file()
        if not self.is_dxf_file():
            raise IOError("'{}' is not a DXF file.".format(self.dxf_file_name))
        self.dxf_file = open_dxf_file()  # restart
        self.get_dxf_encoding()
        self.dxf_file = open_dxf_file()  # restart

    def get_first_dxf_file_name(self):
        dxf_file_names = self.get_dxf_file_names()
        if len(dxf_file_names) > 0:
            return dxf_file_names[0]
        else:
            raise IOError("'{}' has no DXF files.")

    def get_dxf_file_names(self):
        return [name for name in self.zip_archive.namelist() if name.lower().endswith('.dxf')]

    def is_dxf_file(self):
        # TODO: check for DXF file
        return True

    def get_dxf_encoding(self):
        info = dxf_info(self)
        self.encoding = info.encoding

    # interface to TagReader()
    def readline(self):
        next_line = self.dxf_file.readline()
        return ustr(next_line, self.encoding)

    def close(self):
        self.zip_archive.close()


@contextmanager
def ctxZipReader(zip_achive, filename=None):
    zip_reader = ZipReader(zip_achive)
    zip_reader.open(filename)
    yield zip_reader
    zip_reader.close()