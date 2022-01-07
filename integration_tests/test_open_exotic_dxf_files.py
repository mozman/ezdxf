# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf import recover
import os

CP936_FILE = os.path.join(
    ezdxf.EZDXF_TEST_FILES, "ChineseChars_cp936_R2004.dxf"
)


@pytest.mark.skipif(
    not os.path.exists(CP936_FILE), reason=f"File {CP936_FILE} not found"
)
def test_read_plain_cp936_chinese():
    doc = ezdxf.readfile(CP936_FILE)
    assert doc.filename is not None
    assert doc.dxfversion is not None


CP936_ZIP_FILE = os.path.join(
    ezdxf.EZDXF_TEST_FILES, "ChineseChars_cp936_R2004.zip"
)


@pytest.mark.skipif(
    not os.path.exists(CP936_ZIP_FILE),
    reason=f"File {CP936_ZIP_FILE} not found",
)
def test_read_from_zip():
    doc = ezdxf.readzip(CP936_ZIP_FILE)
    assert doc.filename is not None
    assert doc.dxfversion is not None


PROE_FILE = os.path.join(ezdxf.EZDXF_TEST_FILES, "ProE_AC1018.dxf")


@pytest.mark.skipif(
    not os.path.exists(PROE_FILE), reason=f'File "{PROE_FILE}" not found'
)
class TestProE:
    @pytest.fixture
    def filename(self):
        return PROE_FILE

    def test_read_ProE_file(self, filename):
        doc = ezdxf.readfile(filename)
        assert doc.filename is not None
        assert doc.dxfversion is not None

    def test_recover_ProE_file(self, filename):
        doc, auditor = recover.readfile(filename)
        assert doc.filename == filename
        assert doc.dxfversion is not None
        assert len(auditor.errors) == 2
        assert len(auditor.fixes) == 0


FILE_CIVIL_3D = os.path.join(
    ezdxf.EZDXF_TEST_FILES, "AutodeskProducts/Civil3D_2018.dxf"
)


@pytest.mark.skipif(
    not os.path.exists(FILE_CIVIL_3D),
    reason=f'File "{FILE_CIVIL_3D}" not found',
)
class TestCorruptCivil3D:
    """The test file "AutodeskProducts/Civil3D_2018.dxf" contains binary data
    in XRECORDS and is not valid for TrueView 2020!

    """

    @pytest.fixture
    def filename(self):
        return FILE_CIVIL_3D

    def test_readfile_and_preserve_errors_by_surrogate_escape(self, filename):
        doc = ezdxf.readfile(filename, errors="surrogateescape")
        assert doc.filename == filename
        assert doc.dxfversion == "AC1032"

    def test_readfile_and_ignore_errors(self, filename):
        doc = ezdxf.readfile(filename, errors="ignore")
        assert doc.filename == filename
        assert doc.dxfversion == "AC1032"

    def test_readfile_and_raise_exception(self, filename):
        with pytest.raises(UnicodeDecodeError):
            ezdxf.readfile(filename, errors="strict")

        with pytest.raises(UnicodeDecodeError):
            recover.readfile(filename, errors="strict")

    def test_recover(self, filename):
        doc, auditor = recover.readfile(filename, errors="ignore")
        assert doc.filename == filename
        assert doc.dxfversion == "AC1032"
        assert auditor.has_errors is True
        assert len(auditor.errors) == 238, "expected decoding errors"
        assert len(auditor.fixes) == 536


FILE_MAP_3D = os.path.join(
    ezdxf.EZDXF_TEST_FILES, "AutodeskProducts/Map3D_2017.dxf"
)


@pytest.mark.skipif(
    not os.path.exists(FILE_MAP_3D), reason=f'File "{FILE_MAP_3D}" not found'
)
def test_read_map_3d():
    doc = ezdxf.readfile(FILE_MAP_3D)
    assert doc.filename == FILE_MAP_3D
    assert doc.dxfversion == "AC1027"


GERBER_FILE = os.path.join(ezdxf.EZDXF_TEST_FILES, "Gerber.dxf")


@pytest.mark.skipif(
    not os.path.exists(GERBER_FILE), reason=f'File "{GERBER_FILE}" not found'
)
def test_read_gerber_file():
    from ezdxf.lldxf.validator import is_dxf_file

    assert is_dxf_file(GERBER_FILE)

    doc = ezdxf.readfile(GERBER_FILE)
    assert doc.filename == GERBER_FILE
    assert doc.dxfversion == "AC1009"
