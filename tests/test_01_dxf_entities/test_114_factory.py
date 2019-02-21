# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-18

from ezdxf.entities.factory import ENTITY_CLASSES


def test_registered_structural_entities():
    assert 'CLASS' in ENTITY_CLASSES
    assert 'TABLE' in ENTITY_CLASSES
    assert 'BLOCK' in ENTITY_CLASSES
    assert 'ENDBLK' in ENTITY_CLASSES


def test_registered_table_entries():
    assert 'LAYER' in ENTITY_CLASSES
    assert 'LTYPE' in ENTITY_CLASSES
    assert 'STYLE' in ENTITY_CLASSES
    assert 'DIMSTYLE' in ENTITY_CLASSES
    assert 'APPID' in ENTITY_CLASSES
    assert 'UCS' in ENTITY_CLASSES
    assert 'VIEW' in ENTITY_CLASSES
    assert 'VPORT' in ENTITY_CLASSES
    assert 'BLOCK_RECORD' in ENTITY_CLASSES

