import pytest
import glob
import ezdxf
from ezdxf import options
from itertools import chain

DIRS = [
    r"D:\Source\dxftest\AutodeskSamples\*.dxf",
    r"D:\Source\dxftest\AutodeskProducts\*.dxf",
    r"D:\Source\dxftest\CADKitSamples\*.dxf",
    r"D:\Source\dxftest\*.dxf",
]
LEGACY_MODE = False
options.check_entity_tag_structures = True


@pytest.fixture(params=chain(*[glob.glob(d) for d in DIRS]))
def filename(request):
    return request.param


def test_readfile(filename):
    try:
        ezdxf.readfile(filename, legacy_mode=LEGACY_MODE)
    except Exception:
        assert False
    else:
        assert True
