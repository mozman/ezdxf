#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import xref


class TestLoadResources:
    @pytest.fixture(scope="class")
    def sdoc(self):
        doc = ezdxf.new()
        doc.layers.add("FIRST")
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


if __name__ == "__main__":
    pytest.main([__file__])
