# Copyright (c) 2016-2017, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.tools.test import load_section
from ezdxf.sections.objects import ObjectsSection


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


# for fast running tests, just create drawing one time and reset objects sections
@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('AC1015')


@pytest.fixture
def objects(dwg):
    objects = ObjectsSection(load_section(EMPTYSEC, 'OBJECTS'), dwg)
    dwg.sections._sections['OBJECTS'] = objects   # reset objects load_section
    return objects


def get_rootdict(objects):
    rootdict = objects.setup_rootdict()
    objects.setup_objects_management_tables(rootdict)
    return rootdict


def test_setup_rootdict(objects):
    rootdict = objects.setup_rootdict()
    assert 'DICTIONARY' == rootdict.dxftype()


def test_add_new_sub_dict(objects):
    rootdict = get_rootdict(objects)
    new_dict = rootdict.add_new_dict('A_SUB_DICT')
    assert 'DICTIONARY' == new_dict.dxftype()
    assert 0 == len(new_dict)
    assert 'A_SUB_DICT' in rootdict
    assert rootdict.dxf.handle == new_dict.dxf.owner


def test_required_tables_exists(objects):
    rootdict = get_rootdict(objects)
    objects.setup_objects_management_tables(rootdict)

    for table_name in _OBJECT_TABLE_NAMES:
        assert table_name in rootdict, "table %s not found." % table_name


def test_new_plot_style_name_table(objects):
    wrap_handle = objects.drawing.get_dxf_entity
    rootdict = get_rootdict(objects)
    plot_style_name_table = wrap_handle(rootdict["ACAD_PLOTSTYLENAME"])
    assert 'ACDBDICTIONARYWDFLT' == plot_style_name_table.dxftype()
    place_holder = wrap_handle(plot_style_name_table['Normal'])
    assert 'ACDBPLACEHOLDER' == place_holder.dxftype()
    assert place_holder.dxf.owner == plot_style_name_table.dxf.handle


EMPTYSEC = """  0
SECTION
  2
OBJECTS
  0
ENDSEC
"""
