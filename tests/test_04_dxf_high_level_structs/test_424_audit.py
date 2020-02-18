# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.audit import Auditor, AuditError


@pytest.fixture(scope='module')
def dxf():
    return ezdxf.new('R2000')


@pytest.fixture
def auditor(dxf):
    return Auditor(dxf)


@pytest.fixture
def entity(dxf):
    return dxf.modelspace().add_line((0, 0), (100, 0))


def test_target_pointer_ignore_owner(entity, auditor):
    entity.dxf.owner = 'FFFF'
    auditor.check_pointer_target_exist(entity)
    assert len(auditor) == 0, 'should not check owner handle'


def test_color_index(entity, auditor):
    entity.dxf.color = -1
    auditor.check_for_valid_color_index(entity)
    assert len(auditor) == 1
    assert auditor.errors[0].code == AuditError.INVALID_COLOR_INDEX

    auditor.reset()
    entity.dxf.color = 258
    auditor.check_for_valid_color_index(entity)
    assert len(auditor) == 1
    assert auditor.errors[0].code == AuditError.INVALID_COLOR_INDEX


def test_for_valid_layer_name(entity, auditor):
    entity.dxf.layer = 'Invalid/'
    auditor.check_for_valid_layer_name(entity)
    assert len(auditor) == 1
    assert auditor.errors[0].code == AuditError.INVALID_LAYER_NAME


def test_for_existing_owner(entity, auditor):
    entity.dxf.owner = 'FFFFFF'
    auditor.check_owner_exist(entity)
    assert len(auditor) == 1
    assert auditor.errors[0].code == AuditError.INVALID_OWNER_HANDLE


@pytest.fixture
def text(dxf):
    return dxf.modelspace().add_text('TEXT', dxfattribs={'style': 'UNDEFINED'})


def test_for_existing_text_style(text, auditor):
    auditor.check_if_text_style_exists(text)
    assert len(auditor) == 1
    assert auditor.errors[0].code == AuditError.UNDEFINED_TEXT_STYLE
