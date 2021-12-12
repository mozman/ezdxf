#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
"""
Test the ezdxf.entities.objectcollection module, but the tests need
a real implementation: MLeaderStyleCollection

"""
import pytest

import ezdxf


@pytest.fixture(scope="module")
def doc_ro():
    """Returns a read only document"""
    doc = ezdxf.new()
    doc.entitydb.locked = True
    return doc


class TestMagicMethods:
    def test_iter(self, doc_ro):
        assert len(list(doc_ro.mleader_styles)) == 1


if __name__ == '__main__':
    pytest.main([__file__])
