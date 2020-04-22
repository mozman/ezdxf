# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01

from .loader import load, readfile, document
from .fileheader import FileHeader


def export_objects_test_data(doc, filename):
    """
    Writes DWG objects from document `doc` as Base64 encoded strings into a Python compatible text file.

    Args:
        doc: DWG Document
        filename: Python export file name

    """
    import struct
    from textwrap import wrap
    from base64 import b64encode
    from .crc import crc8
    from .objects import dwg_object_data_size

    data = doc.data
    crc_check = False
    version = doc.specs.version
    with open(filename, 'wt') as fp:
        for handle, location in doc.objects_map.items():
            object_start, object_size = dwg_object_data_size(data, location, version)
            object_end = object_start + object_size
            object_data = data[object_start: object_end]
            if crc_check:
                check = struct.unpack_from('<H', data, object_end)
                crc = crc8(object_data, seed=0xc0c1)
                if check != crc:
                    raise ValueError(f'CRC error in object #{handle}.')

            object_name = f'OBJECT_{handle}'
            lines = wrap(b64encode(object_data).decode())
            if len(lines) > 1:
                s = '\n'.join('    "{0}"'.format(line) for line in lines)
                text = f'{object_name} = (\n{s}\n)\n'
            else:
                text = f'{object_name} = "{lines[0]}"\n'
            fp.write(text)
