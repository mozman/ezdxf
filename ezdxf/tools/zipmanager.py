# Purpose: read DXF files from zip archive
# Created: 02.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

__author__ = "mozman <mozman@gmx.at>"

import zipfile
from contextlib import contextmanager

from ezdxf.tools.c23 import ustr
from ezdxf.lldxf.tags import dxf_info
from ezdxf.lldxf.validator import is_dxf_stream

WIN_NEW_LINE = b'\r\n'
NEW_LINE = b'\n'


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
            return self.zip_archive.open(self.dxf_file_name)  # open always in binary mode

        self.zip_archive = zipfile.ZipFile(self.zip_archive_name)
        self.dxf_file_name = dxf_file_name if dxf_file_name is not None else self.get_first_dxf_file_name()
        self.dxf_file = open_dxf_file()

        # reading with standard encoding 'cp1252' - readline() fails if leading comments contain none ascii characters
        if not is_dxf_stream(self):
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

    def get_dxf_encoding(self):
        info = dxf_info(self)
        # since DXF R2007 (AC1021) file encoding is always 'utf-8'
        self.encoding = info.encoding if info.version < 'AC1021' else 'utf-8'

    # interface to tagging layers
    def readline(self):
        next_line = self.dxf_file.readline().replace(WIN_NEW_LINE, NEW_LINE)
        return ustr(next_line, self.encoding)

    def close(self):
        self.zip_archive.close()


@contextmanager
def ctxZipReader(zip_achive, filename=None):
    zip_reader = ZipReader(zip_achive)
    zip_reader.open(filename)
    yield zip_reader
    zip_reader.close()
