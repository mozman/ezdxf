import pytest
import ezdxf

from ezdxf.pp.dxfpp import dxfpp


@pytest.fixture(scope='module', params=['R12', 'R2000'])
def dwg(request):
    return ezdxf.new(request.param)


def test_dxf_drawing_to_html(dwg):
    # checks only if pretty printer is still working
    result = dxfpp(dwg)
    assert len(result) > 0


if __name__ == '__main__':
    pytest.main([__file__])

