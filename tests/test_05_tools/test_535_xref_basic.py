#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import xref


def forward_handles(doc, count: int) -> None:
    for _ in range(count):
        doc.entitydb.next_handle()


class TestLoadResources:
    @pytest.fixture(scope="class")
    def sdoc(self):
        doc = ezdxf.new()
        doc.layers.add("FIRST")
        doc.linetypes.add(  # see also: complex_line_type_example.py
            "SQUARE",
            pattern="A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1",
            description="Square -[]-----[]-----[]-----[]----[]----",
            length=1.45,
        )
        return doc

    def test_loading_a_simple_layer(self, sdoc):
        """This is the basic test to load a simple entity like a layer into a new
        document. It is checked whether all required structures have been created.
        """
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_layers(["first"])
        loader.execute()
        layer = tdoc.layers.get("first")

        assert layer is not sdoc.layers.get("first"), "expected a copy"
        assert layer.dxf.name == "FIRST", "expected the original layer name"
        assert layer.doc is tdoc, "bound to wrong document"
        assert layer.dxf.handle in tdoc.entitydb, "entity not in database"
        assert layer.dxf.owner == tdoc.layers.head.dxf.handle, "invalid owner handle"

    def test_loading_a_complex_linetype(self, sdoc):
        """The next step is to load complex linetypes which requires to load the
        dependent shape file entry too.
        """
        tdoc = ezdxf.new()
        # handles shouldn't be synchronized to the source document!
        forward_handles(tdoc, 10)
        assert (
            sdoc.styles.find_shx("ltypeshp.shx").dxf.font == "ltypeshp.shx"
        ), "expected ltypeshp.shx entry to exist in the source document"

        loader = xref.Loader(sdoc, tdoc)
        loader.load_linetypes(["square"])
        loader.execute()
        ltype = tdoc.linetypes.get("square")
        assert ltype.dxf.name == "SQUARE"
        # do not repeat more tests from test_loading_a_simple_layer()

        style = tdoc.styles.find_shx("ltypeshp.shx")
        assert style.dxf.font == "ltypeshp.shx"
        assert (
            ltype.pattern_tags.get_style_handle() == style.dxf.handle
        ), "expected handle of shape-file 'ltypeshp.shx' in the target document"


if __name__ == "__main__":
    pytest.main([__file__])
