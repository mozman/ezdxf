# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
import pytest
import os

import ezdxf

ZIPFILE = "read_zip_test.zip"


def get_zip_path(zip_file_name):
    test_path = os.path.dirname(__file__)
    zip_path = os.path.join(test_path, zip_file_name)
    return zip_path


@pytest.mark.skipif(
    not os.path.exists(get_zip_path(ZIPFILE)),
    reason="Skipped TestReadZip(): file '{}' not found.".format(
        get_zip_path(ZIPFILE)
    ),
)
def test_read_ac1009():
    dwg = ezdxf.readzip(get_zip_path(ZIPFILE), "AC1009.dxf")
    msp = dwg.modelspace()
    lines = msp.query("LINE")
    assert 255 == len(lines)
