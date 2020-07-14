# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.audit import Auditor, AuditError
from ezdxf.audit.auditor import BlockCycleDetector


@pytest.fixture(scope='module')
def dxf():
    return ezdxf.new('R2000')


@pytest.fixture
def auditor(dxf):
    return Auditor(dxf)


@pytest.fixture
def entity(dxf):
    return dxf.modelspace().add_line((0, 0), (100, 0))


def test_color_index(entity, auditor):
    entity.dxf.color = -1
    auditor.check_entity_color_index(entity)
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.INVALID_COLOR_INDEX

    auditor.reset()
    entity.dxf.color = 258
    auditor.check_entity_color_index(entity)
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.INVALID_COLOR_INDEX


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
    auditor.check_text_style(text)
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.UNDEFINED_TEXT_STYLE


def test_block_cycle_detector_setup():
    doc = ezdxf.new()
    a = doc.blocks.new('a')
    b = doc.blocks.new('b')
    c = doc.blocks.new('c')
    a.add_blockref('b', (0, 0))
    a.add_blockref('c', (0, 0))
    b.add_blockref('c', (0, 0))
    c.add_blockref('a', (0, 0))  # cycle

    detector = BlockCycleDetector(doc)
    assert detector.has_cycle('a') is True
    assert detector.has_cycle('b') is True
    assert detector.has_cycle('c') is True

    auditor = Auditor(doc)
    auditor.check_block_reference_cycles()
    assert len(auditor.errors) == 3  # one entry for each involved block: 'a', 'b', 'c'
    assert auditor.errors[0].code == AuditError.INVALID_BLOCK_REFERENCE_CYCLE
    assert auditor.errors[1].code == AuditError.INVALID_BLOCK_REFERENCE_CYCLE
    assert auditor.errors[2].code == AuditError.INVALID_BLOCK_REFERENCE_CYCLE


def test_block_cycle_detector(dxf):
    detector = BlockCycleDetector(dxf)
    data = {
        'a': set('bcd'),  # no cycle
        'b': set(),
        'c': set('x'),
        'd': set('xy'),
        'e': set('e'),  # short cycle
        'f': set('g'),
        'g': set('h'),
        'h': set('i'),
        'i': set('f'),  # long cycle
        'j': set('k'),
        'k': set('j'),  # short cycle
        'x': set(),
        'y': set(),
    }
    detector.blocks = data
    assert detector.has_cycle('a') is False
    assert detector.has_cycle('b') is False
    assert detector.has_cycle('c') is False
    assert detector.has_cycle('d') is False
    assert detector.has_cycle('e') is True
    assert detector.has_cycle('f') is True
    assert detector.has_cycle('g') is True
    assert detector.has_cycle('h') is True
    assert detector.has_cycle('i') is True
    assert detector.has_cycle('j') is True
    assert detector.has_cycle('k') is True
    assert detector.has_cycle('x') is False
    assert detector.has_cycle('y') is False


def test_broken_block_cycle_detector(dxf):
    detector = BlockCycleDetector(dxf)
    data = {
        'a': set('bcd'),  # 'd' does not exist
        'b': set(),
        'c': set(),
    }
    detector.blocks = data
    assert detector.has_cycle('a') is False
    assert detector.has_cycle('b') is False


def test_fix_invalid_extrusion_vector(dxf, auditor):
    msp = dxf.modelspace()
    circle = msp.add_circle((0, 0), 1)
    circle.dxf.extrusion = (0, 0, 0)
    circle.audit(auditor)
    assert circle.dxf.extrusion == (0, 0, 1)
    assert auditor.fixes[-1].code == AuditError.INVALID_EXTRUSION_VECTOR


def test_fix_invalid_radius(dxf, auditor):
    msp = dxf.modelspace()
    circle = msp.add_circle((0, 0), 0)
    circle.audit(auditor)
    assert circle.is_alive is False
    assert auditor.fixes[-1].code == AuditError.INVALID_RADIUS


def test_fix_invalid_major_axis(dxf, auditor):
    msp = dxf.modelspace()
    ellipse = msp.add_ellipse((0, 0), major_axis=(0, 0, 0), ratio=0.5)
    ellipse.audit(auditor)
    assert ellipse.is_alive is False
    assert auditor.fixes[-1].code == AuditError.INVALID_MAJOR_AXIS

