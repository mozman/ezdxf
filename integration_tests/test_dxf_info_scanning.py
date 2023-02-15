#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import pytest
import ezdxf
from ezdxf import xref, units, const


@pytest.mark.parametrize("fmt", ["asc", "bin"])
@pytest.mark.parametrize("dxfversion", const.versions_supported_by_new)
def test_dxf_info_scanning(dxfversion, fmt, tmp_path):
    drawing_units = units.MM
    doc = ezdxf.new(dxfversion=dxfversion, units=drawing_units)
    doc.encoding = "cp1253"  # Greek
    doc.header["$INSBASE"] = (10, 20, 30)
    filename = tmp_path / f"{dxfversion}.dxf"
    doc.saveas(filename, fmt=fmt)

    info = xref.dxf_info(filename)
    assert info.version == dxfversion
    assert info.encoding == "cp1253"
    assert info.insert_base.isclose((10, 20, 30))

    # DXF R12 does not support the $INSUNITS header variable (checked by BricsCAD 2023)
    if dxfversion == const.DXF12:
        drawing_units = 0
    assert info.insert_units == drawing_units


if __name__ == "__main__":
    pytest.main([__file__])
