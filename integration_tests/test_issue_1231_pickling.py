# Copyright (c) 2025, Matt Broadway
# License: MIT License
from __future__ import annotations
import io
import pickle
from collections.abc import Iterator
from pathlib import Path

import pytest

import ezdxf
from ezdxf.document import Drawing

EXAMPLES = Path(__file__).parent.parent / "examples_dxf"


def example_dxfs() -> Iterator[Path]:
    for item in EXAMPLES.iterdir():
        if item.suffix.lower() == ".dxf":
            yield item


def _to_dxf_str(doc: Drawing) -> str:
    stream = io.StringIO()
    doc.write(stream)
    return stream.getvalue()


def test_document_pickle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ezdxf.options, "write_fixed_meta_data_for_testing", True)

    for item in example_dxfs():
        print(f"testing pickling of {item}")

        doc = ezdxf.readfile(item)
        doc_serialized = pickle.dumps(doc)
        doc_loaded = pickle.loads(doc_serialized)

        assert _to_dxf_str(doc) == _to_dxf_str(doc_loaded)
