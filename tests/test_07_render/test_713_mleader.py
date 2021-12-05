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
        engine.add_mtext_content()
        assert isinstance(engine.entities[0], MText)


if __name__ == '__main__':
    pytest.main([__file__])
