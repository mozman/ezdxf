# Created: 25.04.2014, 2018 rewritten for pytest
# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new('R2000')


def test_create_new_layout(doc):
    new_layout = doc.new_layout('mozman_layout')
    assert 'mozman_layout' == new_layout.name
    assert new_layout.dxf_layout in doc.objects
    assert new_layout.name in doc.rootdict['ACAD_LAYOUT']
    assert new_layout.block_record in doc.block_records
    assert new_layout.block_record.dxf.name in doc.blocks


def test_error_creating_layout_with_existing_name(doc):
    with pytest.raises(ezdxf.DXFValueError):
        doc.new_layout('Model')


def test_create_and_delete_new_layout(doc):
    new_layout = doc.new_layout('mozman_layout_2')
    assert 'mozman_layout_2' == new_layout.name
    assert new_layout.dxf_layout in doc.objects
    assert new_layout.name in doc.rootdict['ACAD_LAYOUT']
    assert new_layout.block_record in doc.block_records
    assert new_layout.block_record.dxf.name in doc.blocks

    layout_name = new_layout.name
    block_name = new_layout.block_record.dxf.name
    doc.delete_layout(layout_name)

    assert new_layout.dxf_layout not in doc.objects
    assert layout_name not in doc.rootdict['ACAD_LAYOUT']
    assert new_layout.block_record.is_alive is False
    assert block_name not in doc.blocks


def test_set_active_layout(doc):
    new_layout = doc.new_layout('mozman_layout_3')
    doc.layouts.set_active_layout('mozman_layout_3')
    assert '*Paper_Space' == new_layout.block_record_name
    assert new_layout.layout_key == doc.block_records.get('*Paper_Space').dxf.handle
