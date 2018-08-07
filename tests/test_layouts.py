import pytest
import ezdxf


@pytest.fixture
def dwg():
    return ezdxf.new('R2000')


def test_create_layout(dwg):
    assert len(dwg.layouts) == 2, "New drawing should have 1 model space and 1 paper space"

    # create a new layout
    layout = dwg.layouts.new('ezdxf')
    assert 'ezdxf' in dwg.layouts
    assert len(layout) == 0, "New layout should contain no entities"

    with pytest.raises(ezdxf.DXFValueError):
        dwg.layouts.new('invalid characters: <>/\":;?*|=`')
    layout.page_setup()  # default paper setup
    assert len(layout) == 1, "missing 'main' viewport entity"


def test_rename_layout(dwg):
    layouts = dwg.layouts
    with pytest.raises(ValueError):
        layouts.rename('Model', 'XXX')

    with pytest.raises(KeyError):
        layouts.rename('mozman', 'XXX')

    layouts.rename('Layout1', 'ezdxf')
    layout = layouts.get('ezdxf')
    assert layout.name == 'ezdxf'
