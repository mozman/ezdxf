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

    def test_import_a_simple_layer(self, sdoc):
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_layers(["first"])
        loader.execute()
        layer = tdoc.layers.get("first")
        assert layer.dxf.name == "FIRST"
        assert layer is not sdoc.layers.get("first"), "expected new layer is a copy"


if __name__ == '__main__':
    pytest.main([__file__])
