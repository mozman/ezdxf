# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01

from .loader import load, readfile
from .fileheader import FileHeader


def export_objects_test_data(doc, filename):
    """
    Writes DWG objects from document `doc` as Base64 encoded strings into a Python compatible text file.

    Args:
        doc: DWG Document
        filename: Python export file name

    """
    from textwrap import wrap
    from base64 import b64encode
    from .crc import crc8
    from .objects import dwg_object_data_size

    with open(filename, 'wt') as fp:
        for handle, object_data in doc.objects_directory.objects.items():
            object_name = f'OBJECT_{handle}'
            lines = wrap(b64encode(object_data).decode())
            if len(lines) > 1:
                s = '\n'.join('    "{0}"'.format(line) for line in lines)
                text = f'{object_name} = (\n{s}\n)\n'
            else:
                text = f'{object_name} = "{lines[0]}"\n'
            fp.write(text)
