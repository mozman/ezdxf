from __future__ import unicode_literals

import pytest

from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.lldxf.validator import structure_validator
from ezdxf.lldxf.const import DXFStructureError

def test_valid_structure():
    tags = list(structure_validator(internal_tag_compiler(
        "  0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n"
    )))
    assert len(tags) == 5


def test_eof_without_lineending():
    tags = list(structure_validator(internal_tag_compiler(
        "  0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF"
    )))
    assert len(tags) == 5


def test_missing_eof():
    with pytest.raises(DXFStructureError):
        list(structure_validator(internal_tag_compiler("999\ncomment")))


def test_missing_endsec():
    with pytest.raises(DXFStructureError):
        list(structure_validator(internal_tag_compiler(
            "  0\nSECTION\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n"
        )))
    with pytest.raises(DXFStructureError):
        list(structure_validator(internal_tag_compiler(
            "  0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nEOF\n"
        )))


def test_missing_endsec_and_eof():
    with pytest.raises(DXFStructureError):
        list(structure_validator(internal_tag_compiler(
            "  0\nSECTION\n"
        )))


def test_missing_section():
    with pytest.raises(DXFStructureError):
        list(structure_validator(internal_tag_compiler(
            "  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n"
        )))



if __name__ == '__main__':
    pytest.main([__file__])
