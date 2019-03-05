# Copyright (c) 2016-2017, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

_OBJECT_TABLE_NAMES = [
    "ACAD_COLOR",
    "ACAD_GROUP",
    "ACAD_LAYOUT",
    "ACAD_MATERIAL",
    "ACAD_MLEADERSTYLE",
    "ACAD_MLINESTYLE",
    "ACAD_PLOTSETTINGS",
    "ACAD_PLOTSTYLENAME",
    "ACAD_SCALELIST",
    "ACAD_TABLESTYLE",
    "ACAD_VISUALSTYLE",
]


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2('R2000')


def test_setup_rootdict(doc):
    rootdict = doc.rootdict
    assert 'DICTIONARY' == rootdict.dxftype()


def test_add_new_sub_dict(doc):
    rootdict = doc.rootdict
    new_dict = rootdict.add_new_dict('A_SUB_DICT')
    assert 'DICTIONARY' == new_dict.dxftype()
    assert 0 == len(new_dict)
    assert 'A_SUB_DICT' in rootdict
    assert rootdict.dxf.handle == new_dict.dxf.owner


def test_required_tables_exists(doc):
    rootdict = doc.rootdict
    for table_name in _OBJECT_TABLE_NAMES:
        assert table_name in rootdict, "table %s not found." % table_name


def test_new_plot_style_name_table(doc):
    rootdict = doc.rootdict
    plot_style_name_table = rootdict["ACAD_PLOTSTYLENAME"]
    assert 'ACDBDICTIONARYWDFLT' == plot_style_name_table.dxftype()
    place_holder = plot_style_name_table['Normal']
    assert 'ACDBPLACEHOLDER' == place_holder.dxftype()
    assert place_holder.dxf.owner == plot_style_name_table.dxf.handle
