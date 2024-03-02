# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import json
import ezdxf
from ezdxf.document import export_json_tags, load_json_tags
from ezdxf.lldxf.tagger import json_tag_loader

@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()

def test_export_json_tags(doc):
    result = export_json_tags(doc, compact=False)
    data = json.loads(result)

    assert isinstance(data, list)
    assert data[0] == [0, "SECTION"]
    assert data[1] == [2, "HEADER"]
    assert data[2] == [9, "$ACADVER"]
    assert data[3] == [1, doc.dxfversion]
    assert data[-1] == [0, "EOF"]


def test_export_compact_json_tags(doc):
    result = export_json_tags(doc, compact=True)
    data = json.loads(result)

    assert isinstance(data, list)
    assert data[0] == [0, "SECTION"]
    assert data[1] == [2, "HEADER"]
    assert data[12] == [9, "$INSBASE"]
    assert data[13] == [10, [0, 0, 0]]
    assert data[-1] == [0, "EOF"]


def test_load_json_tags(doc):
    data_str = export_json_tags(doc, compact=False)
    data = json.loads(data_str)
    tags = list(json_tag_loader(data))

    assert len(tags) == len(data)


def test_load_compact_json_tags():
    data = [[10, [1, 3, 5]]]
    tags = list(json_tag_loader(data))

    assert len(tags) == 3
    assert tags[0] == (10, 1)
    assert tags[1] == (20, 3)
    assert tags[2] == (30, 5)


def test_load_dxf_document_from_json_tags(doc):
    data_str = export_json_tags(doc, compact=False)
    data = json.loads(data_str)
    loaded_doc = load_json_tags(data)

    assert doc.dxfversion == loaded_doc.dxfversion


def test_load_dxf_document_from_compact_json_tags(doc):
    data_str = export_json_tags(doc, compact=True)
    data = json.loads(data_str)
    loaded_doc = load_json_tags(data)

    assert doc.dxfversion == loaded_doc.dxfversion


if __name__ == "__main__":
    pytest.main([__file__])
