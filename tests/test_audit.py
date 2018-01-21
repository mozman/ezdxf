import pytest
import ezdxf
from ezdxf.audit import Auditor, Error


@pytest.fixture(scope='module')
def dxf():
    return ezdxf.new('R2000')


@pytest.fixture
def auditor(dxf):
    return Auditor(dxf)


@pytest.fixture
def entity(dxf):
    return dxf.modelspace().add_line((0, 0), (100, 0))


def test_target_pointer_not_exists(entity, auditor):
    entity.dxf.owner = 'FFFF'
    auditor.check_pointer_target_exists(entity)
    assert len(auditor) == 1
    assert auditor.errors[0].code == Error.POINTER_TARGET_NOT_EXISTS


def test_target_pointer_zero_valid(entity, auditor):
    entity.dxf.owner = '0'
    auditor.check_pointer_target_exists(entity)
    assert len(auditor) == 0, '0 should be a valid target pointer'


def test_target_pointer_zero_invalid(entity, auditor):
    entity.dxf.owner = '0'
    auditor.check_pointer_target_exists(entity, invalid_zero=True)
    assert len(auditor) == 1, '0 should be a valid target pointer'
    assert auditor.errors[0].code == Error.POINTER_TARGET_NOT_EXISTS

