#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest
from pathlib import Path

import ezdxf
from ezdxf.addons import odafc

NO_ODAFC = "ODA File Converter not installed or not found."


def dummy(name):
    with open(name, "wt") as fp:
        fp.write("Hello!\n")
    return name


# noinspection PyPep8Naming
class Test_Convert_ODAFC_Not_Required:
    def test_source_does_not_exist(self):
        with pytest.raises(FileNotFoundError):
            odafc.convert("xxx.dxf")

    def test_source_has_unsupported_extension(self, tmp_path):
        src = dummy(tmp_path / "xxx.err")
        with pytest.raises(odafc.UnsupportedFileFormat):
            odafc.convert(src)

    def test_destination_already_exist(self, tmp_path):
        src = dummy(tmp_path / "xxx.dxf")
        dummy(tmp_path / "xxx.dwg")
        with pytest.raises(FileExistsError):
            odafc.convert(src)

    def test_destination_folder_does_not_exist(self, tmp_path):
        src = dummy(tmp_path / "xxx.dxf")
        with pytest.raises(FileNotFoundError):
            odafc.convert(src, Path("ODAFC_XXX_FOLDER") / "xxx.dwg")

    def test_destination_has_unsupported_extension(self, tmp_path):
        src = dummy(tmp_path / "xxx.dxf")
        dst = tmp_path / "xxx.err"
        with pytest.raises(odafc.UnsupportedFileFormat):
            odafc.convert(src, dst)

    def test_invalid_DXF_version(self, tmp_path):
        src = dummy(tmp_path / "xxx.dxf")
        with pytest.raises(odafc.UnsupportedVersion):
            odafc.convert(src, version="ABC")


def dxf_r12(name):
    doc = ezdxf.new(dxfversion="R12")
    doc.modelspace().add_circle((0, 0), radius=1)
    doc.saveas(name)
    return name


# noinspection PyPep8Naming
@pytest.mark.skipif(not odafc.is_installed(), reason=NO_ODAFC)
class Test_Convert_ODAFC_Required:
    def test_dxf_to_dwg_same_stem(self, tmp_path):
        r12 = dxf_r12(tmp_path / "r12.dxf")
        odafc.convert(r12)
        assert r12.with_suffix(".dwg").exists() is True

    def test_dxf_to_dwg_new_stem(self, tmp_path):
        r12 = dxf_r12(tmp_path / "r12.dxf")
        dest = tmp_path / "r2018.dwg"
        odafc.convert(r12, dest)
        assert dest.exists() is True

    def test_upgrade_dxf_to_r2013(self, tmp_path):
        r12 = dxf_r12(tmp_path / "r12.dxf")
        dest = tmp_path / "r2013.dxf"
        odafc.convert(r12, dest, version="R2013")
        doc = ezdxf.readfile(dest)
        assert doc.acad_release == "R2013"


# noinspection PyPep8Naming
@pytest.mark.skipif(not odafc.is_installed(), reason=NO_ODAFC)
class Test_Export_And_Load_DWG:
    @pytest.fixture
    def doc(self):
        dxf = ezdxf.new(dxfversion="R12")
        dxf.modelspace().add_circle((0, 0), radius=1)
        return dxf

    def test_export_dwg(self, tmp_path, doc):
        dwg_path = tmp_path / "r2013.dwg"
        odafc.export_dwg(doc, str(dwg_path), "R2013")
        assert dwg_path.exists() is True

    def test_read_dwg(self, tmp_path, doc):
        dwg_path = tmp_path / "r2013.dwg"
        odafc.export_dwg(doc, str(dwg_path), "R2013")
        loaded_doc = odafc.readfile(str(dwg_path))
        assert loaded_doc.acad_release == "R2013"


if __name__ == "__main__":
    pytest.main([__file__])
