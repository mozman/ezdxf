# Purpose: read existing example files (all formats), write the imported DXF file and compare the created file with the
# original. Had an ugly bug, which causes a loss of the whole ENTITIES section.
# Created: 03.02.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
import os
import sys
import tempfile
import pytest
from zipfile import ZipFile
from functools import partial
import ezdxf
from ezdxf.lldxf.types import DXFVertex

round_n = partial(round, ndigits=6)

BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'
ZIP_FILE_NAME = os.path.join(BASEDIR, DATADIR, 'rwrcmptest.zip')
pytestmark = pytest.mark.skipif(not os.path.exists(ZIP_FILE_NAME), reason='Zipfile {} not found.'.format(ZIP_FILE_NAME))


def get_filenames(zipname):
    with ZipFile(zipname, 'r') as archive:
        names = archive.namelist()
    return names


@pytest.fixture(params=get_filenames(ZIP_FILE_NAME))
def filename(request):
    return request.param


def copy_by_writing(dwg):
    orig_name = dwg.filename
    name, ext = os.path.splitext(orig_name)
    test_filename = os.path.join(tempfile.gettempdir(), name+'.test.dxf')
    dwg.saveas(test_filename)
    dwg_copy = ezdxf.readfile(test_filename)
    os.remove(test_filename)
    dwg.filename = orig_name
    return dwg_copy


def round_point(point):
    return tuple(round_n(x) for x in point)


def compare_points(point1, point2):
    point1 = round_point(point1)
    point2 = round_point(point2)
    assert point1 == point2


def compare_values(value1, value2):
    def round(value):
        if isinstance(value, float):
            return round_n(value)
        else:
            return value
    value1 = round(value1)
    value2 = round(value2)
    assert value1 == value2


def compare_tag(orig, copy):
    def compare_value(v1, v2):
        return compare_points(v1, v2) if isinstance(orig, DXFVertex) else compare_values(v1, v2)
    assert orig.code == copy.code
    compare_value(orig.value, copy.value)


def compare_len(orig, copy, t=None):
    assert len(orig) == len(copy), "Length mismatch, type: {}".format(type(orig) if t is None else t)


def compare_tag_list(orig, copy):
    orig_tags = list(orig)
    copy_tags = list(copy)
    compare_len(orig_tags, copy_tags, t=type(orig_tags))
    for orig_tag, copy_tag in zip(orig_tags, copy_tags):
        compare_tag(orig_tag, copy_tag)


def compare_header_vars(orig_header, copy_header):
    compare_len(orig_header, copy_header)
    for key in orig_header.varnames():
        if key == '$VERSIONGUID':  # saving creates a new $VERSIONGUID
            continue
        value = orig_header[key]
        copy_value = copy_header[key]
        if isinstance(value, tuple):
            compare_points(value, copy_value)
        else:
            compare_values(value, copy_value)


def compare_entities(orig, copy):
    compare_len(orig, copy)
    for orig_e, copy_e in zip(orig, copy):
        compare_tag_list(orig_e.tags, copy_e.tags)


def compare_blocks(orig, copy):
    def block_name(block):
        return block.name
    for oblock, cblock in zip(sorted(orig, key=block_name), sorted(copy, key=block_name)):
        compare_entities(oblock, cblock)


def compare_tables(orig, copy):
    for orig_t, copy_t in zip(orig, copy):
        compare_entities(orig_t, copy_t)


def compare_dwg(orig, copy):
    compare_header_vars(orig.header, copy.header)
    compare_tables(orig.sections.tables, copy.sections.tables)
    compare_blocks(orig.blocks, copy.blocks)
    compare_entities(orig.entities, copy.entities)
    if 'objects' in orig.sections:
        compare_entities(orig.objects, copy.objects)


@pytest.mark.skipif(sys.version_info < (3, 0), reason="Python 2.7 not supported, because of too much rounding errors.")
def test_rwrc(filename):
    dwg1 = ezdxf.readzip(ZIP_FILE_NAME, filename)
    dwg2 = copy_by_writing(dwg1)
    compare_dwg(dwg1, dwg2)



