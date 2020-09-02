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
options.check_entity_tag_structures = True
files = list(chain(*[glob.glob(os.path.join(EZDXF_TEST_FILES, d)) for d in DIRS]))


@pytest.fixture(params=files)
def filename(request):
    return request.param


def test_readfile(filename):
    try:
        ezdxf.readfile(filename)
    except Exception:
        assert False
    else:
        assert True


if __name__ == '__main__':
    for name in files:
        print(f'Loading file: "{name}"')
        doc = ezdxf.readfile(name)
        auditor = doc.audit()
        if auditor.has_fixes:
            auditor.print_fixed_errors()
        if auditor.has_errors:
            print(f'Unrecoverable errors:')
            auditor.print_error_report()
