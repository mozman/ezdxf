# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new('R2000')


def test_create_new_layout(doc):
    new_layout = doc.new_layout('mozman_layout')
    assert 'mozman_layout' == new_layout.name, 'Has incorrect name'
    assert new_layout.dxf_layout in doc.objects, 'Is not stored in OBJECTS section'
    assert new_layout.name in doc.rootdict['ACAD_LAYOUT'], 'Not stored in LAYOUT dict'
    assert new_layout.block_record.dxf.name in doc.block_records, 'Missing required BLOCK_RECORD'
    assert new_layout.block_record.dxf.name in doc.blocks, 'Missing required BLockLayout'


@pytest.mark.parametrize('name', ['Model', 'MODEL', 'model'])
def test_reserved_model_space_name(doc, name):
    with pytest.raises(ezdxf.DXFValueError):
        doc.new_layout(name)
    with pytest.raises(ezdxf.DXFValueError):
        doc.layouts.delete(name)
    with pytest.raises(ezdxf.DXFValueError):
        doc.layouts.rename(name, 'xxx')
    with pytest.raises(ezdxf.DXFValueError):
        doc.layouts.rename('XXX', name)


def test_case_insensitive_layout_names(doc):
    NAME = 'CaseInSensitive'
    layout = doc.layouts.new(NAME)
    assert layout.name == NAME, 'Expected original case sensitive name'
    assert NAME.upper() in doc.layouts, 'Test for containment should be case insensitive'
    assert layout is doc.layouts.get(NAME.upper()), 'get() should be case insensitive'


def test_create_and_delete_new_layout(doc):
    new_layout = doc.new_layout('mozman_layout_2')
    assert 'mozman_layout_2' == new_layout.name
    assert new_layout.dxf_layout in doc.objects
    assert new_layout.name in doc.rootdict['ACAD_LAYOUT']
    assert new_layout.block_record.dxf.name in doc.block_records
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


def test_rename_layout(doc):
    THE_NEW_NAME = 'TheNewName'
    RENAME_ME = 'RenameMe'
    layout = doc.layouts.new(RENAME_ME)
    doc.layouts.rename(RENAME_ME, THE_NEW_NAME)

    assert RENAME_ME not in doc.layouts, 'Old name not removed'
    assert THE_NEW_NAME in doc.layouts, 'New name not stored'
    assert layout.name == THE_NEW_NAME, 'Layout not renamed'

    # Check if management dict ACAD_LAYOUT is maintained:
    dxf_layouts = doc.rootdict.get('ACAD_LAYOUT')
    assert RENAME_ME not in dxf_layouts
    assert THE_NEW_NAME in dxf_layouts


def test_rename_no_existing_layout(doc):
    with pytest.raises(KeyError):
        doc.layouts.rename('LayoutDoesNotExist', 'XXX')

