#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import os
import pytest
import ezdxf
from ezdxf import recover

BASEDIR = os.path.dirname(__file__)
DATADIR = "data"


@pytest.fixture(params=["duplicate_handles.dxf"])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip(f"File {filename} not found.")
    return filename


def test_recover_duplicate_handles(filename, tmp_path):
    doc, auditor = recover.readfile(filename)
    fixed_dxf_name = tmp_path / "fixed.dxf"
    doc.saveas(fixed_dxf_name)
    assert doc.layers.head.dxf.handle != "2"
    assert doc.linetypes.head.dxf.handle != "4"

    doc2 = ezdxf.readfile(fixed_dxf_name)
    auditor = doc2.audit()
    assert len(auditor.fixes) == 0
    assert len(doc2.modelspace()) == 132


if __name__ == '__main__':
    pytest.main([__file__])
