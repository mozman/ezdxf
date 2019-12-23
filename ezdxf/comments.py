# Created: 23.12.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TextIO, Iterable, Tuple

from ezdxf.lldxf.validator import is_dxf_file
from ezdxf.filemanagement import dxf_file_info
from ezdxf.lldxf.const import DXFStructureError


def from_stream(stream: TextIO, handles: bool = False, structure: bool = False) -> Iterable[Tuple[int, str]]:
    """
    Yields comment tags from text `stream` as (code, value) tuples.

    Args:
        stream: input text stream
        handles: yields also handle tags (code == 5) if `True` as (5, handle) tuples,
                 105 handle of DIMSTYLE entities are ignored!
        structure: yields structure tags (code == 0) if `True` like (0, 'LINE')

    """
    line = 1
    while True:
        try:
            code = stream.readline()
            value = stream.readline()
        except EOFError:
            return
        if code and value:  # StringIO(): empty strings indicates EOF
            try:
                code = int(code)
            except ValueError:
                raise DXFStructureError('Invalid group code "{}" at line {}.'.format(code, line))
            else:
                tag = (code, value.rstrip('\n'))
                if code == 999:  # yield comments
                    yield tag
                elif handles and code == 5:  # yield handles
                    yield tag
                elif structure and code == 0:  # yield structure tags
                    yield tag
                line += 2
        else:
            return


def from_file(filename: str, handles: bool = False, structure: bool = False) -> Iterable[Tuple[int, str]]:
    """
    Yields comment tags from `filename` as (code, value) tuples.

    Args:
        filename: filename as string
        handles: yields also handle tags (code == 5) if `True` as (5, handle) tuples,
                 105 handle of DIMSTYLE entities are ignored!
        structure: yields structure tags (code == 0) if `True` like (0, 'LINE')

    """
    if is_dxf_file(filename):
        info = dxf_file_info(filename)
        with open(filename, mode='rt', encoding=info.encoding) as fp:
            yield from from_stream(fp, handles=handles, structure=structure)
    else:
        raise IOError('File "{}" is not a DXF file.'.format(filename))
