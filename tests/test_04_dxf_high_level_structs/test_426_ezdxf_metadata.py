#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.document import CREATED_BY_EZDXF, WRITTEN_BY_EZDXF


@pytest.fixture(params=["R12", "R2000"])
def doc(request):
    return ezdxf.new(request.param)


def test_created_by_ezdxf_metadata(doc):
    metadata = doc.ezdxf_metadata()
    assert CREATED_BY_EZDXF in metadata
    assert metadata[CREATED_BY_EZDXF].startswith(ezdxf.__version__)


def test_written_by_ezdxf_metadata(doc, tmp_path):
    doc.saveas(tmp_path / "ez.dxf")
    metadata = doc.ezdxf_metadata()
    assert WRITTEN_BY_EZDXF in metadata
    assert metadata[WRITTEN_BY_EZDXF].startswith(ezdxf.__version__)


def test_add_custom_metadata(doc):
    custom = "CUSTOM"
    metadata = doc.ezdxf_metadata()
    metadata[custom] = custom
    assert custom in metadata
    assert metadata[custom] == custom


def test_non_existing_key_raises_key_error(doc):
    metadata = doc.ezdxf_metadata()
    with pytest.raises(KeyError):
        _ = metadata["XY_UNKNOWN"]


def test_modify_metadata(doc):
    modified = "MODIFIED"
    metadata = doc.ezdxf_metadata()
    metadata[CREATED_BY_EZDXF] = modified
    assert metadata[CREATED_BY_EZDXF] == modified


def test_delete_metadata(doc):
    metadata = doc.ezdxf_metadata()
    del metadata[CREATED_BY_EZDXF]
    assert metadata.get(CREATED_BY_EZDXF) == ""
    assert CREATED_BY_EZDXF not in metadata


def test_delete_non_existing_metadata_raises_KeyError(doc):
    metadata = doc.ezdxf_metadata()
    with pytest.raises(KeyError):
        del metadata["XY_UNKNOWN"]


def test_discard_non_existing_metadata_without_exception(doc):
    metadata = doc.ezdxf_metadata()
    metadata.discard("XY_UNKNOWN")
    assert "XY_UNKNOWN" not in metadata


def test_write_and_read_metadata(doc, tmp_path):
    custom = "CUSTOM"
    metadata = doc.ezdxf_metadata()
    del metadata[CREATED_BY_EZDXF]
    metadata[custom] = custom
    doc.saveas(tmp_path / "ez.dxf")

    doc2 = ezdxf.readfile(tmp_path / "ez.dxf")
    metadata2 = doc2.ezdxf_metadata()
    assert metadata2[WRITTEN_BY_EZDXF].startswith(ezdxf.__version__)
    assert CREATED_BY_EZDXF not in metadata2, "should be deleted"
    assert metadata2[custom] == custom, "expected custom metadata"


def test_key_and_data_is_limited_to_254_chars(doc):
    custom = "CUSTOM" * 50
    metadata = doc.ezdxf_metadata()
    metadata[custom] = custom
    assert custom in metadata
    custom254 = custom[:254]
    assert metadata[custom254] == custom254


def test_escape_line_endings_in_key_and_data(doc):
    custom = "CUSTOM\n"
    metadata = doc.ezdxf_metadata()
    metadata[custom] = custom
    assert custom in metadata
    assert (
        metadata[custom] == "CUSTOM\\P"
    ), "line ending should be replaced by \\P"


if __name__ == "__main__":
    pytest.main([__file__])
