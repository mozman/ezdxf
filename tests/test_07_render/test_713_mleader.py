#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.render import mleader
from ezdxf.entities import MText, MLeader, Insert


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


def test_anything(doc):
    engine = mleader.RenderEngine(MLeader(), doc)
    mtext = engine.build_mtext_content()
    assert isinstance(mtext, MText)
    blkref = engine.build_block_content()
    assert isinstance(blkref, Insert)


if __name__ == '__main__':
    pytest.main([__file__])
