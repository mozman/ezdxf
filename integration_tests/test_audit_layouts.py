#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
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
    assert auditor.fixes[0].code == AuditError.ORPHANED_PAPER_SPACE_BLOCK_RECORD_ENTITY
    assert '*Paper_Space99' not in doc.blocks


if __name__ == '__main__':
    pytest.main([__file__])
