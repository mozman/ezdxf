import pytest
from ezdxf.render.arrows import ARROWS


def test_filled_solid_arrow():
    # special name: no name ""
    assert "" in ARROWS
    ARROWS.is_acad_arrow("")


def test_arrow_name():
    assert ARROWS.arrow_name('_CLOSED_FILLED') == ''
    assert ARROWS.arrow_name('') == ''
    assert ARROWS.arrow_name('_DOTSMALL') == 'DOTSMALL'
    assert ARROWS.arrow_name('_boxBlank') == 'BOXBLANK'
    assert ARROWS.arrow_name('EZ_ARROW') == 'EZ_ARROW'
    assert ARROWS.arrow_name('abcdef') == 'abcdef'

