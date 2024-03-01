# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import json
import ezdxf
from ezdxf.document import export_json_tags, load_json_tags
from ezdxf.lldxf.tagger import json_tag_loader


def test_export_json_tags():
    doc = ezdxf.new()
    result = export_json_tags(doc)
    data = json.loads(result)

    assert isinstance(data, list)
    assert data[0] == [0, "SECTION"]
    assert data[1] == [2, "HEADER"]
    assert data[2] == [9, "$ACADVER"]
    assert data[3] == [1, doc.dxfversion]
    assert data[-1] == [0, "EOF"]


def test_load_json_tags():
    doc = ezdxf.new()
    data_str = export_json_tags(doc)
    data = json.loads(data_str)
    tags = list(json_tag_loader(data))

    assert len(tags) == len(data)


def test_load_dxf_document_from_json_tags():
    doc = ezdxf.new()
    data_str = export_json_tags(doc)
    data = json.loads(data_str)
    loaded_doc = load_json_tags(data)

    assert doc.dxfversion == loaded_doc.dxfversion


if __name__ == "__main__":
    pytest.main([__file__])
