import pytest
import ezdxf


@pytest.fixture(params=['R12', 'R2000'])
def dxf(request):
    return ezdxf.new(request.param)


def test_create_vport_table(dxf):
    assert len(dxf.viewports) == 0

    # create a multi-viewport configuration
    # create two entries with same name
    vp1 = dxf.viewports.new('*ACTIVE')
    vp2 = dxf.viewports.new('*ACTIVE')
    assert len(dxf.viewports) == 2

    # get multi-viewport configuration as list
    conf = dxf.viewports.get_multi_config('*Active')
    assert len(conf) == 2

    # check handles
    handles = set([vp1.dxf.handle, vp2.dxf.handle])
    assert conf[0].dxf.handle in handles
    assert conf[1].dxf.handle in handles

    conf = dxf.viewports.get_multi_config('test')
    assert len(conf) == 0

    # delete: ignore not existing configurations
    dxf.viewports.delete_multi_config('test')
    assert len(dxf.viewports) == 2

    # delete multi config
    dxf.viewports.delete_multi_config('*active')
    assert len(dxf.viewports) == 0


