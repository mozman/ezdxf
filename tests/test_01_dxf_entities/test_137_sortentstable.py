# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dxfobj import SortEntsTable


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2('R2000')


def get_entry(table, index):
    return list(table)[index]


def test_sort_entities_table(doc):
    sort_entities_table = doc.objects.create_new_dxf_entity('SORTENTSTABLE', {'block_record_handle': 'FFFF'})
    assert sort_entities_table.dxftype() == 'SORTENTSTABLE'
    assert sort_entities_table.dxf.block_record_handle == 'FFFF'
    assert len(sort_entities_table) == 0
    sort_entities_table.append('AAA', 'BBB')
    assert get_entry(sort_entities_table, 0) == ('AAA', 'BBB')


def test_sort_entities_table_as_list(doc):
    sort_entities_table = doc.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    assert get_entry(sort_entities_table, 0) == ('AAA', 'BBB')
    assert get_entry(sort_entities_table, -1) == ('EEE', 'FFF')

    sort_entities_table.clear()
    assert len(sort_entities_table) == 0


def test_sort_entities_table_to_dict(doc):
    sort_entities_table = doc.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    assert get_entry(sort_entities_table, 2) == ('EEE', 'FFF')

    # simple way to dict()
    d = dict(sort_entities_table)
    assert d['AAA'] == 'BBB'
    assert d['CCC'] == 'DDD'
    assert d['EEE'] == 'FFF'


def test_remove_invalid_handles(doc):
    sort_entities_table = doc.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    sort_entities_table.remove_invalid_handles()
    assert len(sort_entities_table) == 0


def test_remove_handle(doc):
    sort_entities_table = doc.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    sort_entities_table.remove_handle('AAA')
    assert len(sort_entities_table) == 2
    # no exception if handle not exists
    sort_entities_table.remove_handle('FFFF')
    assert len(sort_entities_table) == 2


SORT_ENTITIES_TABLE = """0
SORTENTSTABLE
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbSortentsTable
330
ABBA
331
1
5
A
331
2
5
B
"""


def test_load_table():
    table = SortEntsTable.from_text(SORT_ENTITIES_TABLE)
    assert table.dxf.block_record_handle == 'ABBA'
    assert len(table) == 2
    assert table.table['1'] == 'A'
    assert table.table['2'] == 'B'
