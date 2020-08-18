import pytest

import os
import glob
import ezdxf
from ezdxf import options, EZDXF_TEST_FILES
from itertools import chain

DIRS = [
    "AutodeskSamples/*.dxf",
    "AutodeskProducts/*.dxf",
    "CADKitSamples/*.dxf",
    "dxftest/*.dxf",
]
LEGACY_MODE = False
options.check_entity_tag_structures = True


@pytest.fixture(
    params=chain(*[glob.glob(os.path.join(EZDXF_TEST_FILES, d)) for d in DIRS]))
def filename(request):
    return request.param


def test_readfile(filename):
    try:
        ezdxf.readfile(filename, legacy_mode=LEGACY_MODE)
    except Exception:
        assert False
    else:
        assert True
