import io

import pytest
import ezdxf
from ezdxf.audit import Auditor, AuditError


@pytest.mark.parametrize("version", ["R12", "R2004", "R2018"])
@pytest.mark.parametrize("kind", ["seqend", "vertex"])
def test_owner_repair_is_reported(version, kind):
    doc = ezdxf.new(version)
    modelspace = doc.modelspace()
    polyline = modelspace.add_polyline2d([(0, 0), (10, 0), (10, 10)])
    entity = polyline.seqend if kind == "seqend" else polyline.vertices[0]
    previous_owner = modelspace.block_record_handle
    entity.dxf.owner = previous_owner

    auditor = doc.audit()

    assert entity.dxf.owner == polyline.dxf.handle
    assert auditor.has_fixes
    assert auditor.has_issues
    assert not auditor.errors
    assert len(auditor.fixes) == 1
    fix = auditor.fixes[0]
    assert fix.code == AuditError.INVALID_OWNER_HANDLE
    assert fix.entity is entity
    assert fix.data == previous_owner
    report = io.StringIO()
    auditor.print_fixed_errors(stream=report)
    assert entity.dxf.handle in report.getvalue()
    assert not doc.audit().has_issues


@pytest.mark.parametrize("version", ["R12", "R2004", "R2018"])
@pytest.mark.parametrize("kind", ["POLYLINE", "INSERT"])
def test_seqend_owner_survives_document_roundtrip(version, kind):
    doc = ezdxf.new(version)
    if kind == "POLYLINE":
        entity = doc.modelspace().add_polyline2d([(0, 0), (10, 0), (10, 10)])
    else:
        doc.blocks.new("EXAMPLE")
        entity = doc.modelspace().add_blockref("EXAMPLE", (0, 0))
        entity.add_attrib("TAG", "text")
    assert entity.seqend.dxf.owner == entity.dxf.handle
    stream = io.StringIO()
    doc.write(stream)
    stream.seek(0)
    loaded = ezdxf.read(stream)
    entity = loaded.modelspace().query(kind)[0]
    assert entity.seqend.dxf.owner == entity.dxf.handle
    assert not loaded.audit().has_issues


def test_missing_seqend_is_created_with_correct_owner():
    doc = ezdxf.new()
    polyline = doc.modelspace().add_polyline2d([(0, 0), (10, 0)])
    doc.entitydb.delete_entity(polyline.seqend)
    polyline.seqend = None
    auditor = Auditor(doc)
    polyline.audit(auditor)
    assert polyline.seqend.dxf.owner == polyline.dxf.handle
    assert [fix.code for fix in auditor.fixes] == [AuditError.MISSING_REQUIRED_SEQEND]
    assert not doc.audit().has_issues


@pytest.mark.parametrize("version", ["R12", "R2004", "R2018"])
def test_formatted_vertices_belong_to_polyline(version):
    doc = ezdxf.new(version)
    polyline = doc.modelspace().add_polyline2d([(0, 0), (1, 1)])
    polyline.append_formatted_vertices([(2, 3, 0.5)], format="xyb")
    assert all(vertex.dxf.owner == polyline.dxf.handle for vertex in polyline.vertices)
    assert polyline.vertices[-1].dxf.bulge == 0.5
    assert not doc.audit().has_issues


def test_compound_entities_follow_parent_through_move_and_delete():
    doc = ezdxf.new()
    modelspace = doc.modelspace()
    polyline = modelspace.add_polyline3d([(0, 0, 0), (1, 1, 1)])
    polyline.append_vertex((2, 2, 2))
    polyline.insert_vertices(1, [(3, 3, 3)])
    doc.blocks.new("EXAMPLE")
    insert = modelspace.add_blockref("EXAMPLE", (0, 0))
    insert.add_attrib("TAG", "text")
    target = doc.layouts.new("Target")
    for parent in (polyline, insert):
        children = list(parent.all_sub_entities())
        assert all(child.dxf.owner == parent.dxf.handle for child in children)
        modelspace.move_to_layout(parent, target)
        assert parent.dxf.owner == target.block_record_handle
        assert all(child.dxf.owner == parent.dxf.handle for child in children)
        target.delete_entity(parent)
        assert all(not child.is_alive for child in children)
