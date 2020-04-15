# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from pathlib import Path
from ezdxf.addons.dwg import Document
from ezdxf.addons.dwg.header import load_commands, DESCRIPTION, CMD_SET_VERSION, CMD_SKIP_BITS, CMD_SKIP_NEXT_IF, \
    CMD_SET_VAR, ACAD_LATEST

FILE1 = Path(__file__).parent / '807_1.dwg'
pytestmark = pytest.mark.skipif(not FILE1.exists(), reason=f"Data file '{FILE1}' not present.")


@pytest.fixture(scope='module')
def dwg1() -> bytes:
    return FILE1.read_bytes()


def test_load_classes(dwg1):
    doc = Document(dwg1)
    doc.load()
    assert len(doc.dxf_object_types) == 15
    assert doc.dxf_object_types[500] == 'ACDBDICTIONARYWDFLT'
    assert doc.dxf_object_types[514] == 'LAYOUT'


def test_header_commands():
    assert load_commands('ver: all') == [(CMD_SET_VERSION, ('AC1012', ACAD_LATEST))]
    assert load_commands('ver: R13') == [(CMD_SET_VERSION, ('AC1012', 'AC1012'))]
    assert load_commands('ver: R2000') == [(CMD_SET_VERSION, ('AC1015', 'AC1015'))]
    assert load_commands('ver: R2004+') == [(CMD_SET_VERSION, ('AC1018', ACAD_LATEST))]
    assert load_commands('ver: R13 - R14  # comment') == [(CMD_SET_VERSION, ('AC1012', 'AC1014'))]
    assert load_commands('$TEST: H  # comment') == [(CMD_SET_VAR, ('$TEST', 'H'))]
    assert load_commands('$TEST : BLL') == [(CMD_SET_VAR, ('$TEST', 'BLL'))]
    assert load_commands('skip_bits : 7') == [(CMD_SKIP_BITS, '7')]
    assert load_commands('skip_next_if: 1 == 1\n$TEST : BLL') == [
        (CMD_SKIP_NEXT_IF, '1 == 1'),
        (CMD_SET_VAR, ('$TEST', 'BLL')),
    ]


def test_load_all():
    commands = load_commands(DESCRIPTION)
    assert len(commands) > 0


if __name__ == '__main__':
    pytest.main([__file__])
