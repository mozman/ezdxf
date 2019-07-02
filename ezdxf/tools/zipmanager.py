# Purpose: read DXF files from zip archive
# Created: 02.05.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from typing import BinaryIO, cast, TextIO, List
import zipfile
from contextlib import contextmanager

from ezdxf.lldxf.validator import is_dxf_stream, dxf_info

WIN_NEW_LINE = b'\r\n'
NEW_LINE = b'\n'


class ZipReader:
    def __init__(self, zip_archive_name: str):
        if not zipfile.is_zipfile(zip_archive_name):
            raise IOError("'{}' is not a zip archive.".format(zip_archive_name))
        self.zip_archive_name = zip_archive_name
        self.zip_archive = None  # type: zipfile.ZipFile
        self.dxf_file_name = None  # type: str
        self.dxf_file = None  # type: BinaryIO
        self.encoding = 'cp1252'
        self.dxfversion = 'AC1009'

    def open(self, dxf_file_name: str = None) -> None:
        def open_dxf_file() -> BinaryIO:
            return self.zip_archive.open(self.dxf_file_name)  # open always in binary mode

        self.zip_archive = zipfile.ZipFile(self.zip_archive_name)
        self.dxf_file_name = dxf_file_name if dxf_file_name is not None else self.get_first_dxf_file_name()
        self.dxf_file = open_dxf_file()

        # reading with standard encoding 'cp1252' - readline() fails if leading comments contain none ascii characters
        if not is_dxf_stream(cast(TextIO, self)):
            raise IOError("'{}' is not a DXF file.".format(self.dxf_file_name))
        self.dxf_file = open_dxf_file()  # restart
        self.get_dxf_info()
        self.dxf_file = open_dxf_file()  # restart

    def get_first_dxf_file_name(self) -> str:
        dxf_file_names = self.get_dxf_file_names()
        if len(dxf_file_names) > 0:
            return dxf_file_names[0]
        else:
            raise IOError("'{}' has no DXF files.")

    def get_dxf_file_names(self) -> List[str]:
        return [name for name in self.zip_archive.namelist() if name.lower().endswith('.dxf')]

    def get_dxf_info(self) -> None:
        info = dxf_info(cast(TextIO, self))
        # since DXF R2007 (AC1021) file encoding is always 'utf-8'
        self.encoding = info.encoding if info.version < 'AC1021' else 'utf-8'
        self.dxfversion = info.version

    # required TextIO interface
    def readline(self) -> str:
        next_line = self.dxf_file.readline().replace(WIN_NEW_LINE, NEW_LINE)
        return str(next_line, self.encoding)

    def close(self) -> None:
        self.zip_archive.close()


@contextmanager
def ctxZipReader(zipfilename: str, filename: str = None) -> ZipReader:
    zip_reader = ZipReader(zipfilename)
    zip_reader.open(filename)
    yield zip_reader
    zip_reader.close()
