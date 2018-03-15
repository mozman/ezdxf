import pytest
import glob
import ezdxf
from ezdxf import options
from itertools import chain

DIR1 = r"D:\Source\dxftest\CADKitSamples\*.dxf"
DIR2 = r"D:\Source\dxftest\*.dxf"
LEGACY_MODE = False
options.check_entity_tag_structures = True


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
