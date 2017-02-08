#coding:utf-8
# Author:  mozman <mozman@gmx.at>
# Purpose: read existing example files (all formats), write the imported DXF file and compare the created file with the
# original. Had an ugly bug, which causes a loss of the whole ENTITIES section.
# Created: 03.02.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
import os
import sys
from zipfile import ZipFile
from functools import partial
import ezdxf


SOURCE_ZIP = 'rwrcmptest.zip'
round_n = partial(round, ndigits=6)


def get_filenames():
    with ZipFile(SOURCE_ZIP, 'r') as archive:
        names = archive.namelist()
    return names


def copy_by_writing(dwg):
    orig_name = dwg.filename
    name, ext = os.path.splitext(orig_name)
    test_filename = name+'.test.dxf'
    dwg.saveas(test_filename)
    dwg_copy = ezdxf.readfile(test_filename)
    os.remove(test_filename)
    dwg.filename = orig_name
    return dwg_copy


def compare_codes(code1, code2):
    if code1 != code2:
        return 'group code diff: ({}) != ({})'.format(code1, code2)
    else:
        return ''


def round_point(point):
    return tuple(round_n(x) for x in point)


def compare_points(point1, point2):
    point1 = round_point(point1)
    point2 = round_point(point2)
    if point1 != point2:
        return 'point diff: {} != {}'.format(point1, point2)
    else:
        return ''


def compare_values(value1, value2):
    def round(value):
        if isinstance(value, float):
            return round_n(value)
        else:
            return value
    value1 = round(value1)
    value2 = round(value2)
    if value1 != value2:
        return 'value diff: {} != {}'.format(value1, value2)
    else:
        return ''


def compare_tag(orig, copy):
    def compare_value(v1, v2):
        return compare_points(v1, v2) if isinstance(v1, tuple) else compare_values(v1, v2)
    msg = (
        compare_codes(orig.code, copy.code),
        compare_value(orig.value, copy.value),
    )
    if any(msg):
        return '    code: {} {}'.format(orig.code, ' '.join(msg))
    else:
        return ''


def compare_len(orig, copy, t=None):
    if len(orig) != len(copy):
        if t is None:
            t = type(orig)
        print('ERR: length mismatch: {} != {} type:{}'.format(len(orig), len(copy), t))


def compare_tag_list(orig, copy):
    messages = []
    orig_tags = list(orig)
    copy_tags = list(copy)
    compare_len(orig_tags, copy_tags, t=type(orig_tags))
    for orig_tag, copy_tag in zip(orig_tags, copy_tags):
        msg = compare_tag(orig_tag, copy_tag)
        if msg:
            messages.append(msg)
    if len(messages):
        return '\n'.join(messages)
    else:
        return ''


def compare_header_vars(orig_header, copy_header):
    compare_len(orig_header, copy_header)
    for key in orig_header.varnames():
        msg = ''
        value = orig_header[key]
        copy_value = copy_header[key]
        if isinstance(value, tuple):
            msg += compare_points(value, copy_value)
        else:
            msg += compare_values(value, copy_value)
        if msg:
            print('    {}: {}'.format(key, msg))


def compare_entities(orig, copy):
    compare_len(orig, copy)
    for orig_e, copy_e in zip(orig, copy):
        msg = compare_tag_list(orig_e.tags, copy_e.tags)
        if msg:
            print(msg)


def compare_blocks(orig, copy):
    def block_name(block):
        return block.name
    for oblock, cblock in zip(sorted(orig, key=block_name), sorted(copy, key=block_name)):
        compare_entities(oblock, cblock)


def compare_tables(orig, copy):
    for orig_t, copy_t in zip(orig, copy):
        compare_entities(orig_t, copy_t)


def compare_dwg(orig, copy):
    print('checking: {}'.format(orig.filename))
    print('comparing HEADER')
    compare_header_vars(orig.header, copy.header)
    if 'classes' in orig.sections:
        print('comparing CLASSES')
        compare_entities(orig.sections.classes, copy.sections.classes)
    print('comparing TABLES')
    compare_tables(orig.sections.tables, copy.sections.tables)
    print('comparing BLOCKS')
    compare_blocks(orig.blocks, copy.blocks)
    print('comparing ENTITIES')
    compare_entities(orig.entities, copy.entities)
    if 'objects' in orig.sections:
        print('comparing OBJECTS')
        compare_entities(orig.objects, copy.objects)


def runtest():
    dxfnames = get_filenames()
    for dxfname in dxfnames:
        print('-' * 40)
        dwg1 = ezdxf.readzip(SOURCE_ZIP, dxfname)
        dwg2 = copy_by_writing(dwg1)
        compare_dwg(dwg1, dwg2)


if __name__ == '__main__':
    if sys.version_info < (3, 0, 0):
        print('Read-Write-Read Check: just checking with Python 3, because of so many rounding errors in Python 2.')
    else:
        print('Check if ezdxf writes all drawing content to disk.')
        runtest()


