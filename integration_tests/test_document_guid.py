#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf

CONST_GUID = "{00000000-0000-0000-0000-000000000000}"
FINGERPRINT_GUID = "$FINGERPRINTGUID"
VERSION_GUID = "$VERSIONGUID"


def test_guids_are_created_for_new_docs():
    doc = ezdxf.new()
    assert doc.header[FINGERPRINT_GUID] != CONST_GUID
    assert doc.header[VERSION_GUID] != CONST_GUID


def test_guids_are_preserved_at_loading(tmp_path):
    filepath = tmp_path / "doc1.dxf"
    doc = ezdxf.new()
    doc.saveas(filepath)
    doc1 = ezdxf.readfile(filepath)
    assert doc1.header[FINGERPRINT_GUID] == doc.header[FINGERPRINT_GUID]
    assert doc1.header[VERSION_GUID] == doc.header[VERSION_GUID]


def test_fingerprint_guid_is_preserved_at_export(tmp_path):
    filepath1 = tmp_path / "doc1.dxf"
    filepath2 = tmp_path / "doc2.dxf"
    doc = ezdxf.new()
    doc.saveas(filepath1)
    doc1 = ezdxf.readfile(filepath1)
    doc1.saveas(filepath2)
    doc2 = ezdxf.readfile(filepath2)
    assert doc1.header[FINGERPRINT_GUID] == doc.header[FINGERPRINT_GUID]
    assert doc1.header[FINGERPRINT_GUID] == doc2.header[FINGERPRINT_GUID]


def test_version_guid_changes_at_export(tmp_path):
    filepath1 = tmp_path / "doc1.dxf"
    filepath2 = tmp_path / "doc2.dxf"
    doc = ezdxf.new()
    doc.saveas(filepath1)
    doc1 = ezdxf.readfile(filepath1)
    assert doc1.header[VERSION_GUID] == doc.header[VERSION_GUID]
    # Exporting a new version of this document, $VERSIONGUID must change.
    old_version_guid = doc1.header[VERSION_GUID]
    doc1.saveas(filepath2)  # changes $VERSIONGUID of doc1!
    assert old_version_guid != doc1.header[VERSION_GUID]
    doc2 = ezdxf.readfile(filepath2)
    assert old_version_guid != doc2.header[VERSION_GUID]
    assert doc1.header[VERSION_GUID] == doc2.header[VERSION_GUID]


if __name__ == '__main__':
    pytest.main([__file__])
