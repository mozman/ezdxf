# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
import json
from ezdxf.document import export_to_json


def test_custom_export_to_json():
    doc = ezdxf.new()
    result = export_to_json(doc)
    data = json.loads(result)

    assert isinstance(data, list)
    assert data[0] == [0, "SECTION"]
    assert data[1] == [2, "HEADER"]
    assert data[-1] == [0, "EOF"]


if __name__ == "__main__":
    pytest.main([__file__])
