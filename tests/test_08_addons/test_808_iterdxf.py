# Copyright (c) 2026, Manfred Moitzi
# License: MIT License
import pytest
from pathlib import Path

import ezdxf
from ezdxf.addons import iterdxf

EXAMPLES = Path(__file__).parent.parent.parent / "examples_dxf"


@pytest.fixture(params=["3dface.dxf", "colors.dxf", "VP4.dxf"])
def filename(request):
    path = EXAMPLES / request.param
    if not path.exists():
        pytest.skip(f"example file '{request.param}' not found")
    return path


def test_modelspace_matches_regular_loading(filename):
    """The single pass modelspace loader has to see the same entities as the
    regular document loader.
    """
    expected = [
        (e.dxftype(), e.dxf.handle) for e in ezdxf.readfile(filename).modelspace()
    ]
    entities = [(e.dxftype(), e.dxf.handle) for e in iterdxf.modelspace(filename)]

    assert len(entities) > 0
    assert entities == [e for e in expected if e[0] in iterdxf.SUPPORTED_TYPES]


def test_modelspace_filters_requested_types(filename):
    entities = list(iterdxf.modelspace(filename, types=["LINE"]))
    assert all(e.dxftype() == "LINE" for e in entities)


if __name__ == "__main__":
    pytest.main([__file__])
