# Copyright 2018, Manfred Moitzi
# License: MIT License
import pytest
import os
import ezdxf


FILE_1 = r"D:\Source\dxftest\CADKitSamples\kit-dev-coldfire-xilinx_5213.dxf"


@pytest.mark.skipif(not os.path.exists(FILE_1), reason='test data not present')
def test_kit_dev_coldfire():
    dwg = ezdxf.readfile(FILE_1)
    auditor = dwg.auditor()
    errors = auditor.run()
    assert len(errors) == 0
