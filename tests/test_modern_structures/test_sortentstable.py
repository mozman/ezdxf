# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2000')


def get_entry(table, index):
    return list(table)[index]


def test_sort_entities_table(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {'block_record': 'FFFF'})
    assert sort_entities_table.dxftype() == 'SORTENTSTABLE'
    assert sort_entities_table.dxf.block_record == 'FFFF'
    assert len(sort_entities_table) == 0
    sort_entities_table.append('AAA', 'BBB')
    assert get_entry(sort_entities_table, 0) == ('AAA', 'BBB')


def test_sort_entities_table_as_list(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    assert get_entry(sort_entities_table, 0) == ('AAA', 'BBB')
    assert get_entry(sort_entities_table, -1) == ('EEE', 'FFF')

    sort_entities_table.clear()
    assert len(sort_entities_table) == 0


def test_sort_entities_table_to_dict(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {})
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


def test_remove_invalid_handles(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    sort_entities_table.remove_invalid_handles()
    assert len(sort_entities_table) == 0


def test_remove_handle(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    sort_entities_table.remove_handle('AAA')
    assert len(sort_entities_table) == 2
    # no exception if handle not exists
    sort_entities_table.remove_handle('FFFF')
    assert len(sort_entities_table) == 2
