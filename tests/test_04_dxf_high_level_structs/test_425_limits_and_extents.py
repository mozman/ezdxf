#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf


def test_new_doc_settings_R2000_and_later():
    doc = ezdxf.new()
    extmin = doc.header["$EXTMIN"]
    extmax = doc.header["$EXTMAX"]
    assert extmin == (1e20, 1e20, 1e20)
    assert extmax == (-1e20, -1e20, -1e20)


if __name__ == '__main__':
    pytest.main([__file__])
