import pytest

from ezdxf.lldxf.tagger import string_tagger
from ezdxf.lldxf.validator import structure_validator
from ezdxf.lldxf.const import DXFStructureError
import logging
from io import StringIO

logfile = StringIO()
logging.basicConfig(stream=logfile)


def reset_logfile():
    logfile.seek(0)
    logfile.truncate(0)
    assert logfile.getvalue() == ''


def test_valid_structure():
    tags = list(structure_validator(string_tagger(
        "  0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n"
    )))
    assert len(tags) == 5


def test_missing_eof():
    with pytest.raises(DXFStructureError):
        list(structure_validator(string_tagger("999\ncomment")))


def test_missing_endsec():
    with pytest.raises(DXFStructureError):
        list(structure_validator(string_tagger(
            "  0\nSECTION\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n"
        )))
    with pytest.raises(DXFStructureError):
        list(structure_validator(string_tagger(
            "  0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nEOF\n"
        )))


def test_missing_endsec_and_eof():
    with pytest.raises(DXFStructureError):
        list(structure_validator(string_tagger(
            "  0\nSECTION\n"
        )))


def test_missing_section():
    with pytest.raises(DXFStructureError):
        list(structure_validator(string_tagger(
            "  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n"
        )))


def test_outside_tag():
    reset_logfile()

    tags = list(structure_validator(string_tagger("0\nTABLE\n  0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n")))
    result = logfile.getvalue()
    assert result.startswith('WARNING:ezdxf:DXF Structure Warning')
    assert len(tags) == 6
    reset_logfile()

    tags = list(structure_validator(string_tagger("0\nSECTION\n  0\nENDSEC\n  0\nTABLE\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n")))
    result = logfile.getvalue()
    assert result.startswith('WARNING:ezdxf:DXF Structure Warning')
    assert len(tags) == 6

    reset_logfile()
    # filter=True
    tags = list(structure_validator(
        string_tagger("0\nSECTION\n  0\nENDSEC\n  0\nSECTION\n  0\nENDSEC\n  0\nEOF\n  0\nTABLE\n"),
        filter=True,
    ))
    result = logfile.getvalue()
    assert result.startswith('WARNING:ezdxf:DXF Structure Warning')
    assert len(tags) == 5
    assert tags[-1] == (0, 'EOF')


if __name__ == '__main__':
    pytest.main([__file__])
