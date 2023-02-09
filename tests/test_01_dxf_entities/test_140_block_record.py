#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.audit import Auditor


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


def test_duplicate_handle_loading_error(doc):
    msp = doc.modelspace()
    p1 = msp.add_point((0, 0))
    p2 = msp.add_point((0, 0))
    count = len(msp)
    # Simulate loading error with same handle for two entities!
    p2.dxf.handle = p1.dxf.handle
    auditor = Auditor(doc)
    block_record = doc.block_records.get("*Model_Space")
    block_record.audit(auditor)
    assert len(auditor.fixes) == 1
    assert len(msp) == count-1
    assert p2.is_alive, "entity should not be destroyed"


if __name__ == '__main__':
    pytest.main([__file__])
