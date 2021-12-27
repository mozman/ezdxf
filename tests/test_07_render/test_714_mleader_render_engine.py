#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.math import Vec2
from ezdxf.render import mleader
from ezdxf.entities import MText, MultiLeader, Insert


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


def make_multi_leader(doc) -> MultiLeader:
    style = doc.mleader_styles.get("Standard")
    ml = MultiLeader.new(doc=doc)
    ml.dxf.style_handle = style.dxf.handle
    return ml


class TestRenderEngine:
    """The RenderEngine renders DXF primitives from a MULTILEADER entity."""

    @pytest.fixture
    def ml_mtext(self, doc):
        ml = make_multi_leader(doc)
        builder = mleader.MultiLeaderMTextBuilder(ml)
        builder.set_content("line")
        builder.build(insert=Vec2(0, 0))
        return ml

    def test_add_mtext_content(self, ml_mtext):
        engine = mleader.RenderEngine(ml_mtext, ml_mtext.doc)
        engine.add_mtext_content()
        assert isinstance(engine.entities[0], MText)


if __name__ == "__main__":
    pytest.main([__file__])
