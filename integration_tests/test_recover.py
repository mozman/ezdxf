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
    with open(filename01, 'rb') as fp:
        return list(recover.safe_tag_loader(fp))


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
    sections = recover._rebuild_sections(tags01)
    expected = sum(int(tag == (0, 'SECTION')) for tag in tags01)
    orphans = sections.pop()
    assert len(sections) == expected
    assert len(orphans) == 4
