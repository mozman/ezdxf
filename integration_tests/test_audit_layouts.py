#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest
import os
import ezdxf
from ezdxf.audit import AuditError


def test_find_orphaned_layouts():
    doc = ezdxf.new()
    # Construct an orphaned LAYOUT entity:
    # Use proper owner, else we get audit error: INVALID_OWNER_HANDLE
    owner = doc.rootdict['ACAD_LAYOUT'].dxf.handle
    layout = doc.objects.new_entity(
        'LAYOUT', dxfattribs={'name': 'Orphaned', 'owner': owner})

    auditor = doc.audit()
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.ORPHANED_LAYOUT_ENTITY
    assert layout.is_alive is False


def test_find_orphaned_block_record():
    doc = ezdxf.new()
    # Construct an orphaned paperspace layout BLOCK_RECORD:
    doc.blocks.new('*Paper_Space99')
    auditor = doc.audit()
    assert len(auditor.fixes) == 1
    assert auditor.fixes[
               0].code == AuditError.ORPHANED_PAPER_SPACE_BLOCK_RECORD_ENTITY
    assert '*Paper_Space99' not in doc.blocks


@pytest.fixture
def MODEL_path() -> str:
    return os.path.join(os.path.dirname(__file__), 'data', 'MODEL.dxf')


def test_load_MODEL(MODEL_path):
    doc = ezdxf.readfile(MODEL_path)
    msp = doc.modelspace()
    assert msp.dxf.name == 'MODEL', 'Keep original uppercase name.'
    assert 'MODEL' in doc.rootdict['ACAD_LAYOUT']
    assert 'MODEL' in doc.layouts, 'Check name as case insensitive string'
    assert 'Model' in doc.layouts, 'Check name as case insensitive string'


if __name__ == '__main__':
    pytest.main([__file__])
