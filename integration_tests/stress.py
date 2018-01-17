import pytest
import glob
import ezdxf
from itertools import chain

DIR1 = r"D:\Source\dxftest\CADKitSamples\*.dxf"
DIR2 = r"D:\Source\dxftest\*.dxf"
LEGACY_MODE = False


@pytest.fixture(params=chain(glob.glob(DIR1), glob.glob(DIR2)))
def filename(request):
    return request.param


def test_readfile(filename):
    try:
        dwg = ezdxf.readfile(filename, legacy_mode=LEGACY_MODE)
    except Exception:
        assert False
    else:
        assert True
