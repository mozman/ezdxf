# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf


@pytest.fixture(params=['R12', 'R2000'], scope='module')
def dwg(request):
    return ezdxf.new(request.param)


def test_copy_simple_entity(dwg):
    msp = dwg.modelspace()
    psp = dwg.layout('Layout1')
    circle = msp.add_circle(center=(2, 3), radius=1.5)
    assert circle.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    new_circle = circle.copy_to_layout(psp)
    assert new_circle.dxf.paperspace == 1
    assert len_msp == len(msp)
    assert len_psp + 1 == len(psp)


def test_copy_polyline_entity(dwg):
    msp = dwg.modelspace()
    psp = dwg.layout('Layout1')
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])
    assert polyline.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    new_polyline = polyline.copy_to_layout(psp)
    assert new_polyline.dxf.paperspace == 1
    assert len_msp == len(msp)
    assert len_psp + 1 == len(psp)  # just POLYLINE, attached entities do not appear in a layout space


def test_move_simple_entity(dwg):
    msp = dwg.modelspace()
    psp = dwg.layout('Layout1')
    circle = msp.add_circle(center=(2, 3), radius=1.5)
    assert circle.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    circle.move_to_layout(psp)
    assert circle.dxf.paperspace == 1
    assert len_msp - 1 == len(msp)
    assert len_psp + 1 == len(psp)


def test_move_polyline_to_paperspace(dwg):
    msp = dwg.modelspace()
    psp = dwg.layout('Layout1')
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])
    assert polyline.dxf.paperspace == 0
    len_msp = len(msp)
    len_psp = len(psp)
    polyline.move_to_layout(psp)
    assert polyline.dxf.paperspace == 1
    assert len_msp - 1 == len(msp)
    assert len_psp + 1 == len(psp)
    for vertex in polyline.vertices():
        assert vertex.dxf.paperspace == polyline.dxf.paperspace
    if dwg.dxfversion > 'AC1009':  # DXF R2000+
        for vertex in polyline.vertices():
            assert vertex.dxf.owner == polyline.dxf.owner


def test_move_polyline_to_block(dwg):
    msp = dwg.modelspace()
    block = dwg.blocks.new('Test1')
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)])
    assert polyline.dxf.paperspace == 0
    len_msp = len(msp)
    len_block = len(block)
    polyline.move_to_layout(block)
    assert polyline.dxf.paperspace == 0
    assert len_msp - 1 == len(msp)
    assert len_block + 1 == len(block)
    for vertex in polyline.vertices():
        assert vertex.dxf.paperspace == polyline.dxf.paperspace
    if dwg.dxfversion > 'AC1009':  # DXF R2000+
        for vertex in polyline.vertices():
            assert vertex.dxf.owner == polyline.dxf.owner
