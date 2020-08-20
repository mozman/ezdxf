# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import os
import pytest
from ezdxf import recover
from ezdxf.lldxf.tagger import tag_compiler, ascii_tags_loader

BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'


@pytest.fixture(params=['recover01.dxf'])
def filename01(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip('File {} not found.'.format(filename))
    return filename


@pytest.fixture
def tags01(filename01):
    tool = recover.Recover()
    with open(filename01, 'rb') as fp:
        return list(tool.load_tags(fp))


def test_bytes_loader(filename01):
    with open(filename01, 'rb') as fp:
        tags = list(recover.bytes_loader(fp))
    assert len(tags) == 14736


def test_safe_tag_loader(filename01):
    with open(filename01, 'rt', encoding='cp1252') as fp:
        expected = list(tag_compiler(iter(ascii_tags_loader(fp))))

    with open(filename01, 'rb') as fp:
        tags = list(recover.safe_tag_loader(fp))

    assert len(tags) == len(expected)
    assert tags[:100] == tags[:100]


def test_rebuild_sections(tags01):
    tool = recover.Recover()
    sections = tool.rebuild_sections(tags01)
    expected = sum(int(tag == (0, 'SECTION')) for tag in tags01)
    orphans = sections.pop()
    assert len(sections) == expected
    assert len(orphans) == 4


def test_build_section_dict(tags01):
    tool = recover.Recover()
    sections = tool.rebuild_sections(tags01)
    tool.load_section_dict(sections)
    assert len(tool.section_dict) == 2
    header = tool.section_dict['HEADER'][0]
    assert len(header) == 6
    assert header[0] == (0, 'SECTION')
    assert header[1] == (2, 'HEADER')
    assert len(tool.section_dict['ENTITIES']) == 1505


def test_readfile_01(filename01):
    doc = recover.readfile(filename01)
    assert doc.dxfversion == 'AC1009'
    auditor = doc.audit()
    assert auditor.has_errors is False
