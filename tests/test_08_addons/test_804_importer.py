# Copyright (c) 2013-2019, Manfred Moitzi
# License: MIT
import pytest
import os
import ezdxf
from ezdxf.addons.importer import Importer


def save_source_dwg(dwg, filename):
    if not os.path.exists(filename):
        dwg.saveas(filename)


def create_source_drawing(version):
    dwg = ezdxf.new(version)
    # complex shape linetype
    dwg.linetypes.new('BORDER', dxfattribs={
        'description': 'Border square ----[]-----[]----[]-----[]----[]--',
        'length': 1.45,
        'pattern': 'A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1',
    })
    # complex text linetype
    dwg.linetypes.new('GAS', dxfattribs={
        'description': 'Gas ----GAS----GAS----GAS----GAS----GAS----GAS--',
        'length': 1,
        'pattern': 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
    })
    dwg.layers.new('Test', dxfattribs={'color': 17})
    dwg.layers.new('TestConflict', dxfattribs={'color': 18})
    msp = dwg.modelspace()
    msp.add_line((0, 0), (10, 0))
    msp.add_circle((0, 0), radius=5)
    msp.add_line((0, 1), (10, 1), dxfattribs={'linetype': 'BORDER'})
    msp.add_line((0, 2), (10, 2), dxfattribs={'linetype': 'GAS'})
    msp.add_blockref("TestBlock", insert=(0, 0))
    msp.add_blockref("ConflictBlock", insert=(0, 0))
    build_block(dwg, "TestBlock")
    build_block(dwg, "ConflictBlock")
    block = build_block(dwg, "RefToConflictBlock")
    block.add_blockref('ConflictBlock', insert=(0, 0))
    return dwg


def create_target_drawing(version):
    dwg = ezdxf.new(version)
    dwg.layers.new('TestConflict', dxfattribs={'color': 19})
    conflict_block = build_block(dwg, "ConflictBlock")
    conflict_block.add_circle((1, 1), radius=7)
    return dwg


def build_block(dwg, name):
    block = dwg.blocks.new(name=name)
    block.add_line((0, 0), (10, 0))
    block.add_circle((0, 0), radius=5)
    return block


SRC_DWG = {
    "R12": create_source_drawing("R12"),
    "R2000": create_source_drawing("R2000"),
}


@pytest.fixture(params=['R12', 'R2000'])
def importer(request):
    version = request.param
    source = SRC_DWG[version]
    target = create_target_drawing(version)
    return Importer(source, target)


def test_import_simple_modelspace(importer):
    importer.import_modelspace()
    importer.finalize()

    source_entities = list(importer.source.modelspace())
    target_entities = list(importer.target.modelspace())
    assert len(source_entities) == len(target_entities)


def test_import_tables_without_conflict(importer):
    importer.import_table('layers')
    importer.finalize()

    layer = importer.target.layers.get('Test')
    assert layer.get_color() == 17


def test_import_tables_with_conflict_discard(importer):
    importer.import_table('layers', replace=False)
    importer.finalize()

    layer = importer.target.layers.get('TestConflict')
    assert layer.get_color() == 19


def test_import_tables_with_conflict_replace(importer):
    importer.import_table('layers', replace=True)
    importer.finalize()

    layer = importer.target.layers.get('TestConflict')
    assert layer.get_color() == 18


def test_import_block_without_conflict(importer):
    importer.import_block('TestBlock')
    importer.finalize()

    block = importer.target.blocks.get('TestBlock')
    block_entities = list(block)
    assert len(block_entities) == 2


def test_import_block_with_conflict_discard(importer):
    importer.import_blocks(['ConflictBlock'], rename=False)
    importer.finalize()

    block = importer.target.blocks.get('ConflictBlock')
    block_entities = list(block)
    assert len(block_entities) == 3


def test_import_block_with_conflict_rename(importer):
    importer.import_blocks(['ConflictBlock'], rename=True)
    importer.finalize()

    block = importer.target.blocks.get('ConflictBlock0')
    block_entities = list(block)
    assert len(block_entities) == 2


def test_import_block_with_conflict_rename_resolve_block_ref(importer):
    importer.import_blocks(['ConflictBlock'], rename=True)
    inserts = importer.source.query('INSERT')
    importer.import_entities(inserts)
    importer.finalize()

    msp = list(importer.target.modelspace())
    assert msp[1].dxf.name == 'ConflictBlock0'


def test_import_block_with_conflict_rename_resolve_block_ref_inside_block_def(importer):
    src_blocks = [block.name for block in importer.source.blocks if not block.is_any_layout]
    importer.import_blocks(src_blocks, rename=True)
    importer.finalize()

    block = importer.target.blocks.get('RefToConflictBlock')
    block_entities = list(block)
    block_ref_to_conflict_block = block_entities[2]
    assert block_ref_to_conflict_block.dxf.name == 'ConflictBlock0'


@pytest.mark.parametrize('name, style_name, font', [
    ('BORDER', '', 'ltypeshp.shx'),  # shape file entry has no name
    ('GAS', 'Standard', 'txt'),  # text
])
def test_import_entities_using_complex_linetypes(importer, name, style_name, font):
    lines = importer.source.query(f'LINE[linetype=="{name}"]')
    assert len(lines) == 1, 'Required test LINE does not exist.'

    importer.import_entities(lines)
    importer.finalize()

    assert name in importer.target.linetypes, f'Linetype {name } not imported.'
    ltype = importer.target.linetypes.get(name)

    if importer.source.dxfversion == 'AC1009':
        return  # complex line types are not supported by DXF R12

    style_handle = ltype.pattern_tags.get_style_handle()
    assert style_handle != '0', 'Invalid shape file handle.'

    style = importer.target.entitydb[style_handle]
    assert style.dxf.name == style_name
    assert style.dxf.font == font


def test_import_polyline():
    source = ezdxf.new()
    source.modelspace().add_polyline3d([(0, 0), (3, 0), (3, 3), (0, 3)])
    target = ezdxf.new()
    importer = Importer(source, target)
    importer.import_modelspace()
    tpoly = target.modelspace()[0]
    assert len(tpoly.vertices) == 4
    assert tpoly.seqend is not None
    assert tpoly.seqend.dxf.layer == tpoly.dxf.layer


def test_import_insert_with_attribs():
    source = ezdxf.new()
    source.blocks.new('Test')
    sinsert = source.modelspace().add_blockref('Test', insert=(0, 0))
    sinsert.add_attrib('A1', 'text1')
    sinsert.add_attrib('A2', 'text2')
    target = ezdxf.new()
    importer = Importer(source, target)
    importer.import_modelspace()
    tinsert = target.modelspace()[0]
    assert len(tinsert.attribs) == 2
    assert tinsert.seqend is not None
    assert tinsert.seqend.dxf.layer == tinsert.dxf.layer
