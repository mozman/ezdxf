#  Copyright (c) 2025, Manfred Moitzi
#  License: MIT License
import pytest
from pathlib import Path

import ezdxf
from ezdxf import xref
from ezdxf.document import Drawing

DATA = Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def doc1():
    return ezdxf.readfile(DATA / "issue_1359_1.dxf")


@pytest.fixture(scope="module")
def doc2():
    return ezdxf.readfile(DATA / "issue_1359_2.dxf")


@pytest.fixture(scope="module")
def mdoc(doc1: Drawing, doc2: Drawing):
    merged_doc = ezdxf.new(dxfversion=doc1.dxfversion)
    xref.load_modelspace(doc1, merged_doc, conflict_policy=xref.ConflictPolicy.KEEP)
    xref.load_modelspace(doc2, merged_doc, conflict_policy=xref.ConflictPolicy.KEEP)
    return merged_doc


def test_mdoc_contains_block_definition_1(mdoc: Drawing):
    assert "1" in mdoc.blocks


def test_merged_doc_contains_the_source_block_references(mdoc: Drawing):
    msp = mdoc.modelspace()
    assert len(msp) == 2
    assert all(e.dxftype() == "INSERT" for e in msp)


def test_copied_insert_entities_referencing_the_same_block(mdoc: Drawing):
    """Both INSERT entities should reference the BLOCK '1'."""
    msp = mdoc.modelspace()
    assert all(e.dxf.name == "1" for e in msp)


if __name__ == "__main__":
    pytest.main([__file__])
