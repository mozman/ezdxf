from __future__ import unicode_literals

import pytest

from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.sections import load_dxf_structure


def validator(text):
    tags = internal_tag_compiler(text)
    return load_dxf_structure(tags)


def test_valid_structure():
    sections = validator("  0\nSECTION\n 2\nHEADER\n  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF\n")
    assert len(sections) == 2
    assert len(sections['HEADER']) == 1  # ENDSEC is not present
    assert len(sections['CLASSES']) == 1  # ENDSEC is not present


def test_eof_without_lineending():
    sections = validator("  0\nSECTION\n 2\nHEADER\n  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF")
    assert len(sections) == 2
    assert len(sections['HEADER']) == 1  # ENDSEC is not present
    assert len(sections['CLASSES']) == 1  # ENDSEC is not present


def test_missing_eof():
    with pytest.raises(DXFStructureError):
        validator("999\ncomment")


def test_missing_endsec():
    with pytest.raises(DXFStructureError):
        validator("  0\nSECTION\n 2\nHEADER\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF\n")

    with pytest.raises(DXFStructureError):
        validator("  0\nSECTION\n 2\nHEADER\n  0\nSECTION\n  2\nCLASSES\n  0\nEOF\n")


def test_missing_endsec_and_eof():
    with pytest.raises(DXFStructureError):
        validator("  0\nSECTION\n 2\nHEADER\n  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n")


def test_missing_section():
    with pytest.raises(DXFStructureError):
        validator("  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF\n")
