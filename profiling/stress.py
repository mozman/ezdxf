#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest

import os
import glob
import ezdxf
from ezdxf import recover
from ezdxf import EZDXF_TEST_FILES
from itertools import chain

DIRS = [
    "AutodeskSamples/*.dxf",
    "AutodeskProducts/*.dxf",
    "CADKitSamples/*.dxf",
    "*.dxf",
]

files = list(chain(*[glob.glob(os.path.join(EZDXF_TEST_FILES, d)) for d in DIRS]))


@pytest.mark.parametrize('filename', files)
def test_readfile(filename):
    try:
        recover.readfile(filename)
    except ezdxf.DXFStructureError:
        pytest.fail(f'{filename}: DXFStructureError in recover mode.')
    else:
        assert True


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.WARNING)
    for name in files:
        print(f'Loading file: "{name}"')
        try:
            doc = ezdxf.readfile(name)
            auditor = doc.audit()
        except ezdxf.DXFStructureError:
            print('Regular loading function failed, using recover mode.')
            doc, auditor = recover.readfile(name)
        if auditor.has_errors:
            print(f'Found {len(auditor.errors)} unrecoverable error(s).')
        if auditor.has_fixes:
            print(f'Fixed {len(auditor.fixes)} error(s).')
