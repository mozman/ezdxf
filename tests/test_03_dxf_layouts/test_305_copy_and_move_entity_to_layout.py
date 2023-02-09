# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


def test_copy_simple_entity(doc):
    msp = doc.modelspace()
    psp = doc.layout("Layout1")
    circle = msp.add_circle(center=(2, 3), radius=1.5)
    assert circle.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    new_circle = circle.copy_to_layout(psp)
    assert new_circle.dxf.paperspace == 1
    assert len_msp == len(msp)
    assert len_psp + 1 == len(psp)


def test_copy_polyline_entity(doc):
    msp = doc.modelspace()
    psp = doc.layout("Layout1")
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])
    assert polyline.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    new_polyline = polyline.copy_to_layout(psp)
    assert new_polyline.dxf.paperspace == 1
    assert len_msp == len(msp)
    assert len_psp + 1 == len(
        psp
    )  # just POLYLINE, attached entities do not appear in a layout space


def test_move_simple_entity(doc):
    msp = doc.modelspace()
    psp = doc.layout("Layout1")
    circle = msp.add_circle(center=(2, 3), radius=1.5)
    assert circle.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    circle.move_to_layout(psp)
    assert circle.dxf.paperspace == 1
    assert len_msp - 1 == len(msp)
    assert len_psp + 1 == len(psp)


def test_move_polyline_to_paperspace(doc):
    msp = doc.modelspace()
    psp = doc.layout("Layout1")
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])
    assert polyline.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    polyline.move_to_layout(psp)
    assert polyline.dxf.paperspace == 1
    assert len_msp - 1 == len(msp)
    assert len_psp + 1 == len(psp)
    for vertex in polyline.vertices:
        assert vertex.dxf.paperspace == polyline.dxf.paperspace
        assert (
            vertex.dxf.owner == polyline.dxf.handle
        ), "POLYLINE is owner of VERTEX entities"


def test_move_polyline_to_block(doc):
    msp = doc.modelspace()
    block = doc.blocks.new("Test1")
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])
    assert polyline.dxf.paperspace == 0
    len_msp = len(msp)
    len_block = len(block)
    polyline.move_to_layout(block)
    assert polyline.dxf.paperspace == 0
    assert len_msp - 1 == len(msp)
    assert len_block + 1 == len(block)
    for vertex in polyline.vertices:
        assert vertex.dxf.paperspace == polyline.dxf.paperspace
        assert (
            vertex.dxf.owner == polyline.dxf.handle
        ), "POLYLINE is owner of VERTEX entities"


def test_move_from_block_to_block(doc):
    source_block = doc.blocks.new("Test2")
    target_block = doc.blocks.new("Test3")
    polyline = source_block.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])

    polyline.move_to_layout(target_block)
    assert len(source_block) == 0
    assert len(target_block) == 1
    # and back by layout.move_to_layout()
    target_block.move_to_layout(polyline, source_block)
    assert len(source_block) == 1
    assert len(target_block) == 0
