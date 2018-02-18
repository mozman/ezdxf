# Copyright 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import os
import pytest
import ezdxf
from ezdxf.lldxf.tagger import low_level_tagger
from ezdxf.lldxf.loader import load_dxf_structure

BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'


@pytest.fixture(params=["POLI-ALL210_12.dxf"])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip('File {} not found.'.format(filename))
    return filename


def test_check_R12_has_handles(filename):
    dwg = ezdxf.readfile(filename)
    assert dwg.header['$HANDLING'] > 0
    for entity in dwg.modelspace():
        assert int(entity.dxf.handle, 16) > 0


def test_write_R12_without_handles(filename, tmpdir):
    dwg = ezdxf.readfile(filename)
    dwg.header['$HANDLING'] = 0
    export_path = str(tmpdir.join("dxf_r12_without_handles.dxf"))
    dwg.saveas(export_path)

    # can't check with ezdxf.readfile(), because handles automatically enabled
    with open(export_path) as f:
        tagger = low_level_tagger(f)
        sections = load_dxf_structure(tagger)
        for entity in sections['ENTITIES']:
            with pytest.raises(ezdxf.DXFValueError):  # has no handles
                entity.get_handle()

        for entity in sections['TABLES']:
            if entity[0] != (0, 'DIMSTYLE'):
                with pytest.raises(ezdxf.DXFValueError):  # has no handles
                    entity.get_handle()
            else:  # special DIMSTYLE entity
                assert len(entity.find_all(105)) == 0, 'remove handle group code 105'
                assert len(entity.find_all(5)) == 1, 'do not remove group code 5'
