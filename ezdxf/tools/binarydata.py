# Purpose: binary data management
# Created: 03.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .c23 import PY3
from ..lldxf.tags import CompressedTags
from array import array

BINARY_DATA_CODES = frozenset(range(310, 320))
ENTITIES_WITH_PROXY_GRAPHIC = frozenset(['MESH', 'BODY', 'REGION', '3DSOLID', 'SURFACE', 'PLANESURFACE', 'HELIX',
                                         'TABLE'])
SUBCLASSES_WITH_BINARY_DATA = frozenset(['AcDbProxyEntity', 'AcDbProxyObject', 'AcDbOleFrame', 'AcDbOle2Frame',
                                         'AcDbVbaProject', 'AcDbXrecord'])


def compress_binary_data(tags):
    dxftype = tags.dxftype()
    for subclass in tags.subclasses[1:]:
        name = subclass[0].value
        if name == 'AcDbEntity' and dxftype in ENTITIES_WITH_PROXY_GRAPHIC:
            # 310: proxy entity graphics data
            _compress_binary_tags(subclass)
        if name in SUBCLASSES_WITH_BINARY_DATA:
            # 310: binary object data
            _compress_binary_tags(subclass)


def _compress_binary_tags(tags):
    compress_tasks = _collect_compress_tasks(tags)
    if len(compress_tasks):
        _execute_compress_tasks(tags, compress_tasks)


def _collect_compress_tasks(tags):
    compress_tasks = []
    tag_collector = []
    collect_code = None
    for index, tag in enumerate(tags):
        if collect_code is not None:
            if tag.code == collect_code:
                tag_collector.append(tag)
                tags[index] = None
            else:
                compress_tasks.append((collect_code, tag_collector))
                collect_code = None
                tag_collector = []  # new list is essential, because old list is stored in compress_tasks
        if collect_code is None and tag.code in BINARY_DATA_CODES:
            collect_code = tag.code
            tag_collector.append(tag)
            tags[index] = "COMPRESSED_{}".format(len(compress_tasks))  # mark insert position
    if len(tag_collector):
        compress_tasks.append((collect_code, tag_collector))
    return compress_tasks


def _execute_compress_tasks(tags, tasks):
    if not len(tasks):
        return
    for num, task in enumerate(tasks):
        code, binary_tags = task
        if len(binary_tags):
            compressed_tag = CompressedTags(code, binary_tags)
            index = tags.index("COMPRESSED_{}".format(num))
            tags[index] = compressed_tag
    tags[:] = (tag for tag in tags if tag is not None)  # remove delete tags


def binary_encoded_data_to_bytes(data):
    byte_array = array('B' if PY3 else b'B')
    for text in data:
        byte_array.extend(int(text[index:index+2], 16) for index in range(0, len(text), 2))
    return byte_array.tostring()

