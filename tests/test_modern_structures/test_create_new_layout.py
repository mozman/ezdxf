# Created: 25.04.2014, 2018 rewritten for pytest
# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dxf_ac1015():
    return ezdxf.new('AC1015')


def is_layout_in_object_section(layout, dwg):
    return layout.dxf.handle in dwg.objects


def is_layout_in_dxf_layout_management_table(layout, dwg):
    dxf_layout_management_table_handle = dwg.rootdict['ACAD_LAYOUT']
    dxf_layout_management_table = dwg.dxffactory.wrap_handle(dxf_layout_management_table_handle)
    return layout.name in dxf_layout_management_table


def block_record_for_layout_exist(layout, dwg):
    for block_record in dwg.sections.tables.block_records:
        if block_record.dxf.layout == layout.dxf.handle:
            return True
    return False


def block_for_layout_exist(layout, dwg):
    for block in dwg.blocks:
        if block.block_record_handle == layout.layout_key:
            return True
    return False


def create_new_layout(dwg, name):
    dwg.new_layout(name)
    return dwg.layouts.get(name)


def test_create_new_layout(dxf_ac1015):
    new_layout = create_new_layout(dxf_ac1015, 'mozman_layout')
    assert 'mozman_layout' == new_layout.name
    assert is_layout_in_object_section(new_layout, dxf_ac1015) is True
    assert is_layout_in_dxf_layout_management_table(new_layout, dxf_ac1015) is True
    assert block_record_for_layout_exist(new_layout, dxf_ac1015) is True
    assert block_for_layout_exist(new_layout, dxf_ac1015) is True


def test_error_creating_layout_with_existing_name(dxf_ac1015):
    with pytest.raises(ezdxf.DXFValueError):
        dxf_ac1015.new_layout('Model')


def test_create_and_delete_new_layout(dxf_ac1015):
    new_layout = create_new_layout(dxf_ac1015, 'mozman_layout_2')
    assert 'mozman_layout_2' == new_layout.name
    assert is_layout_in_object_section(new_layout, dxf_ac1015) is True
    assert is_layout_in_dxf_layout_management_table(new_layout, dxf_ac1015) is True
    assert block_record_for_layout_exist(new_layout, dxf_ac1015) is True
    assert block_for_layout_exist(new_layout, dxf_ac1015) is True

    dxf_ac1015.delete_layout(new_layout.name)

    assert is_layout_in_object_section(new_layout, dxf_ac1015) is False
    assert is_layout_in_dxf_layout_management_table(new_layout, dxf_ac1015) is False
    assert block_record_for_layout_exist(new_layout, dxf_ac1015) is False
    assert block_for_layout_exist(new_layout, dxf_ac1015) is False
    assert new_layout.dxf.handle not in dxf_ac1015.entitydb


def test_set_active_layout(dxf_ac1015):
    new_layout = create_new_layout(dxf_ac1015, 'mozman_layout_3')
    dxf_ac1015.layouts.set_active_layout('mozman_layout_3')
    assert '*Paper_Space' == new_layout.block_record_name
    assert new_layout.layout_key == dxf_ac1015.get_active_layout_key()
