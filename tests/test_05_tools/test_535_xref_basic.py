#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import xref
from ezdxf.tools.standards import setup_dimstyle


def forward_handles(doc, count: int) -> None:
    for _ in range(count):
        doc.entitydb.next_handle()


class TestLoadResourcesWithoutNamingConflicts:
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
        doc.linetypes.add(
            "GAS",
            pattern='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
            description="Gas ----GAS----GAS----GAS----GAS----GAS----GAS--",
            length=1,
        )
        arial = doc.styles.add("ARIAL", font="Arial.ttf")
        arial.set_extended_font_data(family="Arial", italic=False, bold=True)
        doc.layers.add("SECOND", linetype="SQUARE")
        dimstyle = setup_dimstyle(
            doc, "EZ_M_100_H25_CM", style="ARIAL", name="TestDimStyle"
        )
        dimstyle.dxf.dimltype = "GAS"
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

    def test_loading_a_shape_linetype(self, sdoc):
        """Load a complex linetype with shapes which requires to load the dependent
        shape-file entry too.
        """
        tdoc = ezdxf.new()
        # handles shouldn't be synchronized to the source document!
        forward_handles(tdoc, 7)
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
        pattern_style_handle = ltype.pattern_tags.get_style_handle()
        assert pattern_style_handle != "0"
        assert (
            pattern_style_handle == style.dxf.handle
        ), "expected handle of shape-file 'ltypeshp.shx' as pattern style handle"

    def test_loading_a_text_linetype(self, sdoc):
        """Load a complex linetype which contains text, the handle to the text style
        should point to the STANDARD text style in the target document.
        """
        tdoc = ezdxf.new()
        # handles shouldn't be synchronized to the source document!
        forward_handles(tdoc, 11)
        loader = xref.Loader(sdoc, tdoc)
        loader.load_linetypes(["gas"])
        loader.execute()
        ltype = tdoc.linetypes.get("gas")
        assert ltype.dxf.name == "GAS"
        # do not repeat more tests from test_loading_a_simple_layer()

        style = tdoc.styles.get("STANDARD")
        pattern_style_handle = ltype.pattern_tags.get_style_handle()
        assert pattern_style_handle != "0"
        assert (
            pattern_style_handle == style.dxf.handle
        ), "expected handle of text style STANDARD as pattern style handle"

    def test_loading_layer_with_complex_linetype(self, sdoc):
        """Loading a layer which references a complex linetype that also requires
        loading of an additional text style.
        """
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_layers(["second"])
        loader.execute()
        layer = tdoc.layers.get("second")
        assert layer.dxf.name == "SECOND", "expected the original layer name"

        # Test if required resources are loaded:
        ltype = tdoc.linetypes.get(layer.dxf.linetype)
        assert ltype.dxf.name == "SQUARE", "expected linetype SQUARE in target doc"
        assert tdoc.styles.find_shx("ltypeshp.shx") is not None

    def test_loading_a_text_style_with_extended_font_data(self, sdoc):
        """The extended font data is stored into XDATA section of the STYLE table entry."""
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_text_styles(["arial"])
        loader.execute()
        arial = tdoc.styles.get("arial")
        assert arial.dxf.name == "ARIAL", "expected text style ARIAL in target doc"

        family, italic, bold = arial.get_extended_font_data()
        assert family == "Arial"
        assert italic is False
        assert bold is True

    def test_loading_dimstyle(self, sdoc):
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_dim_styles(["TestDimStyle"])
        loader.execute()

        dimstyle = tdoc.dimstyles.get("TestDimStyle")
        assert dimstyle.dxf.name == "TestDimStyle"

        assert dimstyle.dxf.dimtxsty == "ARIAL"
        arial = tdoc.styles.get("arial")
        assert arial.dxf.name == "ARIAL", "expected text style ARIAL in target doc"

        assert dimstyle.dxf.dimltype == "GAS"
        ltype = tdoc.linetypes.get("GAS")
        assert ltype.dxf.name == "GAS", "expected linetype GAS in target doc"


if __name__ == "__main__":
    pytest.main([__file__])
