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
    layout.paper_setup()  # default paper setup
    assert len(layout) == 1, "missing 'main' viewport entity"


