#  Copyright (c) 2020-2023, Manfred Moitzi
#  License: MIT License
import pytest
import pathlib
import random
from ezdxf import recover
from ezdxf.audit import AuditError
from ezdxf.lldxf.tagger import tag_compiler, ascii_tags_loader

DATA = pathlib.Path(__file__).parent / "data"
RECOVER1 = "recover01.dxf"
RECOVER2 = "recover02.dxf"
CC_DXFLIB = "cc_dxflib.dxf"
EMPTY_HANDLES = "empty_handles.dxf"


def fullpath(name):
    filepath = DATA / name
    if not filepath.exists():
        pytest.skip(f"File {filepath} not found.")
    return str(filepath)


@pytest.fixture
def tags01():
    filename = fullpath(RECOVER1)
    tool = recover.Recover()
    with open(filename, "rb") as fp:
        return list(tool.load_tags(fp, errors="ignore"))


def test_bytes_loader():
    filename = fullpath(RECOVER1)
    with open(filename, "rb") as fp:
        tags = list(recover.bytes_loader(fp))
    assert len(tags) == 14736


def test_safe_tag_loader():
    filename = fullpath(RECOVER1)
    with open(filename, "rt", encoding="cp1252") as fp:
        expected = list(tag_compiler(iter(ascii_tags_loader(fp))))

    with open(filename, "rb") as fp:
        tags = list(recover.safe_tag_loader(fp))

    assert len(tags) == len(expected)
    assert tags[:100] == tags[:100]


def test_rebuild_sections(tags01):
    tool = recover.Recover()
    sections = tool.rebuild_sections(tags01)
    expected = sum(int(tag == (0, "SECTION")) for tag in tags01)
    orphans = sections.pop()
    assert len(sections) == expected
    assert len(orphans) == 4


def test_build_section_dict(tags01):
    tool = recover.Recover()
    sections = tool.rebuild_sections(tags01)
    tool.load_section_dict(sections)
    assert len(tool.section_dict) == 2
    header = tool.section_dict["HEADER"][0]
    assert len(header) == 6
    assert header[0] == (0, "SECTION")
    assert header[1] == (2, "HEADER")
    assert len(tool.section_dict["ENTITIES"]) == 1505


def test_readfile_recover01_dxf():
    doc, auditor = recover.readfile(fullpath(RECOVER1))
    assert doc.dxfversion == "AC1009"
    assert auditor.has_errors is False


@pytest.fixture
def tags02():
    filename = fullpath(RECOVER2)
    tool = recover.Recover()
    with open(filename, "rb") as fp:
        return list(tool.load_tags(fp, errors="ignore"))


def test_rebuild_tables(tags02):
    recover_tool = recover.Recover()
    sections = recover_tool.rebuild_sections(tags02)
    recover_tool.load_section_dict(sections)
    tables = recover_tool.section_dict.get("TABLES")
    random.shuffle(tables)

    tables = recover_tool.rebuild_tables(tables)
    assert tables[0] == [(0, "SECTION"), (2, "TABLES")]
    assert tables[1][0] == (0, "TABLE")
    assert tables[1][1] == (2, "VPORT")
    assert tables[2][0] == (0, "VPORT")
    assert tables[3][0] == (0, "ENDTAB")

    assert tables[4][0] == (0, "TABLE")
    assert tables[4][1] == (2, "LTYPE")
    assert tables[5][0] == (0, "LTYPE")
    assert tables[8][0] == (0, "ENDTAB")

    assert tables[-5][0] == (0, "TABLE")
    assert tables[-5][1] == (2, "BLOCK_RECORD")
    assert tables[-4][0] == (0, "BLOCK_RECORD")
    assert tables[-1][0] == (0, "ENDTAB")


def test_readfile_recover02_dxf():
    doc, auditor = recover.readfile(fullpath(RECOVER2))
    assert doc.dxfversion == "AC1032"
    assert auditor.has_errors is False

    # Auditor should restore deleted BLOCK-RECORD table head:
    blkrec_head = doc.block_records.head
    assert blkrec_head.dxf.handle is not None
    assert blkrec_head.dxf.handle in doc.entitydb

    # Auditor should update/fix BLOCK_RECORD entries owner handle:
    for entry in doc.block_records:
        assert (
            entry.dxf.owner == blkrec_head.dxf.handle
        ), "Auditor() should update table-entry owner handle."

    # Auditor should restore invalid VPORT table-head owner handle:
    vport_head = doc.viewports.head
    assert (
        vport_head.dxf.owner == "0"
    ), "Auditor() should repair invalid table-head owner handle."

    # Auditor should fix invalid VPORT table-entry owner handle:
    vport = doc.viewports.get("*Active")[0]
    assert (
        vport.dxf.owner == vport_head.dxf.handle
    ), "Auditor() should update table-entry owner handle."


def test_read_cc_dxflib_file():
    doc, auditor = recover.readfile(fullpath(CC_DXFLIB))
    codes = {fix.code for fix in auditor.fixes}
    assert AuditError.REMOVED_UNSUPPORTED_SECTION in codes
    assert AuditError.REMOVED_UNSUPPORTED_TABLE in codes
    msp = doc.modelspace()
    polyline = msp.query("POLYLINE").first
    assert polyline is not None


def test_readfile_empty_handles_dxf():
    doc, auditor = recover.readfile(fullpath(EMPTY_HANDLES))
    msp = doc.modelspace()
    assert doc.dxfversion == "AC1009"
    assert auditor.has_errors is False
    assert len(msp.query("LINE")) == 8
    assert len(msp.query("*[layer=='GEOMETRY-CUTTING']")) == 4
    assert len(msp.query("*[layer=='GEOMETRY-ENGRAVING']")) == 4


def test_decode_dxf_unicode_automatically():
    # The test file contains the layer name: "Tschüss mit \U+00FC"
    doc, _ = recover.readfile(fullpath("dxf_unicode.dxf"))
    assert any("Tschüss mit ü" == layer.dxf.name for layer in doc.layers) is True


def test_recover_layout_broken_links_1():
    """
    Links broken in one direction.

    LAYOUT entities have invalid handles to block records but BLOCK_RECORDs have
    valid handles to LAYOUT entities.
    """
    doc, _ = recover.readfile(fullpath("layout_broken_links.dxf"))
    assert len(doc.layouts) == 3
    msp = doc.modelspace()
    assert msp.block_record.dxf.name == "*Model_Space"
    layout1 = doc.layouts.get("Layout1")
    assert layout1.block_record.dxf.name == "*Paper_Space"
    layout2 = doc.layouts.get("Layout2")
    assert layout2.block_record.dxf.name == "*Paper_Space0"


def test_recover_layout_broken_links_2():
    """
    Links broken in both directions.
    
    LAYOUT entities have invalid handles to block records and BLOCK_RECORDs have no 
    LAYOUT handles.
    """
    doc, _ = recover.readfile(fullpath("layout_broken_links_2.dxf"))
    assert len(doc.layouts) == 3
    msp = doc.modelspace()
    assert msp.block_record.dxf.name == "*Model_Space"
    layout1 = doc.layouts.get("Layout1")
    assert layout1.block_record.dxf.name == "*Paper_Space"
    layout2 = doc.layouts.get("Layout2")
    assert layout2.block_record.dxf.name == "*Paper_Space0"


def test_recover_layout_missing_block_record():
    """BLOCK_RECORD for Layout2 does not exist."""
    doc, _ = recover.readfile(fullpath("layout_missing_block_record.dxf"))
    assert len(doc.layouts) == 3
    layout1 = doc.layouts.get("Layout1")
    assert layout1.block_record.dxf.name == "*Paper_Space"

    layout2 = doc.layouts.get("Layout2")
    block_record2 = layout2.block_record
    assert block_record2.dxf.name == "*Paper_Space0"

    block2 = doc.blocks.get(block_record2.dxf.name)
    assert block2.name == block_record2.dxf.name


def test_recover_layout_missing_block_definition():
    """BLOCK definition for Layout2 does not exist."""
    doc, _ = recover.readfile(fullpath("layout_missing_block_definition.dxf"))
    assert len(doc.layouts) == 3
    block_name = "*Paper_Space0"

    block_def = doc.blocks.get(block_name)
    block_record = block_def.block_record
    assert block_record.dxf.name == block_name

    layout2 = doc.layouts.get("Layout2")
    assert layout2.block_record_name == block_name
    assert layout2.block_record is block_record


if __name__ == "__main__":
    pytest.main([__file__])
