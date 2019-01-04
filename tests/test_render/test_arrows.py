import pytest
from ezdxf.render.arrows import ARROWS


def test_filled_solid_arrow():
    # special name: no name ""
    assert "" in ARROWS
    ARROWS.is_acad_arrow("")

