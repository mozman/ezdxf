#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, cast
import pytest
import ezdxf
from ezdxf import recover
from ezdxf.entities import MText

COLUMNS_R2007 = 'data/mtext_columns_R2007.dxf'
COLUMNS_R2018 = 'data/mtext_columns_R2018.dxf'


def load_mtext_entities(name: str) -> Iterable[MText]:
    doc = ezdxf.readfile(name)
    msp = doc.modelspace()
    entities = msp.query('MTEXT')
    return entities


def recover_mtext_entities(name: str) -> Iterable[MText]:
    doc, auditor = recover.readfile(name)
    msp = doc.modelspace()
    entities = msp.query('MTEXT')
    return entities


@pytest.fixture(scope='module', params=['load', 'recover'])
def r2007(request):
    if request.param == 'load':
        return load_mtext_entities(COLUMNS_R2007)
    elif request.param == 'recover':
        return recover_mtext_entities(COLUMNS_R2007)


@pytest.fixture(scope='module', params=['load', 'recover'])
def r2018(request):
    if request.param == 'load':
        return load_mtext_entities(COLUMNS_R2018)
    elif request.param == 'recover':
        return recover_mtext_entities(COLUMNS_R2018)


def test_load_mtext_columns_from_dxf_r2007(r2007):
    for mtext in r2007:
        assert mtext.has_columns is True
        columns = mtext.columns
        assert columns.count == 3
        assert len(columns.linked_columns) == 2
        db = mtext.doc.entitydb
        for column in columns.linked_columns:
            column = cast(MText, column)
            assert column.is_alive is True
            assert column.has_columns is False, "should not have columns"
            assert column.dxf.handle in db, \
                "should be stored in the entity database"
            assert column.dxf.owner is None, \
                "should not be stored in a layout"


def test_load_mtext_columns_from_dxf_r2018(r2018):
    for mtext in r2018:
        assert mtext.has_columns is True
        columns = mtext.columns
        assert columns.count == 3
        assert len(columns.linked_columns) == 0


if __name__ == '__main__':
    pytest.main([__file__])
