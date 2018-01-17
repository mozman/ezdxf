# Copyright 2018, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf


@pytest.fixture(params=['custom_blocks.dxf'])
def filename(request):
    filename = request.param
    if not os.path.exists(filename):
        filename = os.path.join('integration_tests', filename)
        if not os.path.exists(filename):
            pytest.skip('File {} not found.'.format(filename))
    return filename


def test_block_import(filename, tmpdir):
    source_dwg = ezdxf.readfile(filename)
    target_dwg = ezdxf.new(source_dwg.dxfversion)
    importer = ezdxf.Importer(source_dwg, target_dwg)
    importer.import_blocks(query='CustomBlock1')
    importer.import_modelspace_entities()
    filename = str(tmpdir.join('custom_blocks_import.dxf'))
    try:
        target_dwg.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), target_dwg.dxfversion))
    assert os.path.exists(filename)


