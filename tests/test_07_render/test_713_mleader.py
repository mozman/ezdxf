#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
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


class TestMultiLeaderBuilder:
    """The MultiLeaderBuilder is a construction tool to build the MULTILEADER
    entity and the necessary geometry information stored in the entity.
    """
    def test_set_mtext_content(self, doc):
        ml = make_multi_leader(doc)
        builder = mleader.MultiLeaderBuilder(ml)
        builder.set_mtext_content("line1")
        builder.render(insert=(0, 0))
        assert ml.context.mtext is not None
        assert ml.context.mtext.default_content == "line1"


class TestRenderEngine:
    """The RenderEngine renders DXF primitives from a MULTILEADER entity.
    """
    @pytest.fixture
    def ml_mtext(self, doc):
        ml = make_multi_leader(doc)
        builder = mleader.MultiLeaderBuilder(ml)
        builder.set_mtext_content('line')
        builder.render(insert=(0, 0))
        return ml

    def test_add_mtext_content(self, ml_mtext):
        engine = mleader.RenderEngine(ml_mtext, ml_mtext.doc)
        engine.add_mtext_content()
        assert isinstance(engine.entities[0], MText)


if __name__ == '__main__':
    pytest.main([__file__])
