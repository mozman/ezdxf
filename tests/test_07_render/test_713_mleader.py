#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.render import mleader
from ezdxf.entities import MText, MLeader, Insert


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


class TestRenderEngine:
    def test_mtext_builder(self, doc):
        engine = mleader.RenderEngine(MLeader(), doc)
        content = engine.build_mtext_content()
        assert isinstance(content[0], MText)

    def test_block_builder(self, doc):
        engine = mleader.RenderEngine(MLeader(), doc)
        content = engine.build_block_content()
        assert isinstance(content[0], Insert)


if __name__ == '__main__':
    pytest.main([__file__])
