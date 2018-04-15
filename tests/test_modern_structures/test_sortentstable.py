# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2000')


def test_sort_entities_table(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {'block_record': 'FFFF'})
    assert sort_entities_table.dxftype() == 'SORTENTSTABLE'
    assert sort_entities_table.dxf.block_record == 'FFFF'
    assert len(sort_entities_table) == 0
    sort_entities_table.append('AAA', 'BBB')
    assert sort_entities_table[0] == ('AAA', 'BBB')


def test_sort_entities_table_as_list(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    assert sort_entities_table[0] == ('AAA', 'BBB')
    assert sort_entities_table[-1] == ('EEE', 'FFF')

    sort_entities_table[1] = ('ABC', 'DEF')
    assert len(sort_entities_table) == 3
    assert sort_entities_table[1] == ('ABC', 'DEF')

    del sort_entities_table[:2]
    assert len(sort_entities_table) == 1
    assert sort_entities_table[0] == ('EEE', 'FFF')
    assert sort_entities_table[-1] == ('EEE', 'FFF')

    sort_entities_table.clear()
    assert len(sort_entities_table) == 0


def test_sort_entities_table_to_dict(dwg):
    sort_entities_table = dwg.objects.create_new_dxf_entity('SORTENTSTABLE', {})
    sort_entities_table.set_handles([
        ('AAA', 'BBB'), ('CCC', 'DDD'), ('EEE', 'FFF'),
    ])
    assert len(sort_entities_table) == 3
    assert sort_entities_table[2] == ('EEE', 'FFF')

    # simple way to dict()
    d = dict(sort_entities_table)
    assert d['AAA'] == 'BBB'
    assert d['CCC'] == 'DDD'
    assert d['EEE'] == 'FFF'




