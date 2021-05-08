# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.addons.drawing.properties import RenderContext, is_valid_color
from ezdxf.entities import Layer, factory
from ezdxf.lldxf import const


@pytest.fixture(scope='module')
def doc():
    d = ezdxf.new(setup=True)
    d.layers.new('Test', dxfattribs={
        'color': 5,  # blue: 0000ff
        'linetype': 'DOT',
        'lineweight': 70,  # 0.70
    })
    msp = d.modelspace()
    msp.add_line((0, 0), (1, 0), dxfattribs={
        'color': 256,  # by layer
        'linetype': 'BYLAYER',
        'lineweight': -1,  # by layer
        'layer': 'Test',
    })
    msp.add_line((0, 0), (1, 0), dxfattribs={
        'color': 1,  # red: ff0000
        'linetype': 'DASHED',
        'lineweight': 50,  # 0.50
        'layer': 'Test',
    })
    blk = d.blocks.new('MyBlock')
    blk.add_line((0, 0), (1, 0), dxfattribs={
        'color': 0,  # by block
        'linetype': 'BYBLOCK',
        'lineweight': -2,  # by block
        'layer': 'Test',
    })
    blk.add_line((0, 0), (1, 0), dxfattribs={
        'color': 1,  # red: ff0000
        'linetype': 'DASHED',
        'lineweight': 50,  # 0.50
        'layer': 'Test',
    })
    blk.add_line((0, 0), (1, 0), dxfattribs={
        'color': 256,  # by layer
        'linetype': 'BYLAYER',
        'lineweight': -1,  # by layer
        'layer': 'Test',
    })
    msp.add_blockref('MyBlock', insert=(0, 0), dxfattribs={
        'color': 3,  # green: 00ff00
        'linetype': 'CENTER',
        'lineweight': 13,  # 0.13
    })
    return d


def test_load_default_ctb(doc):
    ctx = RenderContext(doc, ctb='color.ctb')
    assert bool(ctx.plot_styles) is True
    assert ctx.plot_styles[1].color == (255, 0, 0)


def test_new_ctb(doc):
    ctx = RenderContext(doc)
    assert bool(ctx.plot_styles) is True
    assert ctx.plot_styles[1].color == (255, 0, 0)


def test_resolve_entity_visibility():
    doc = ezdxf.new()
    layout = doc.modelspace()
    doc.layers.new(name='visible', dxfattribs={'color': 0})
    doc.layers.new(name='invisible',
                   dxfattribs={'color': -1})  # color < 0 => invisible
    doc.layers.new(name='frozen',
                   dxfattribs={'flags': Layer.FROZEN})  # also invisible
    doc.layers.new(name='noplot', dxfattribs={
        'plot': 0})  # visible in the CAD application but not when exported

    for export_mode in (False, True):
        ctx = RenderContext(layout.doc, export_mode=export_mode)

        text = layout.add_text('a', {'invisible': 0, 'layer': 'non_existent'})
        assert ctx.resolve_visible(text) is True

        text = layout.add_text('a', {'invisible': 0, 'layer': 'visible'})
        assert ctx.resolve_visible(text) is True

        for layer in ['invisible', 'frozen']:
            text = layout.add_text('a', {'invisible': 0, 'layer': layer})
            assert ctx.resolve_visible(text) is False

        for layer in ['non_existent', 'visible', 'invisible', 'frozen',
                      'noplot']:
            text = layout.add_text('a', {'invisible': 1, 'layer': layer})
            assert ctx.resolve_visible(text) is False

    ctx = RenderContext(layout.doc, export_mode=False)
    text = layout.add_text('a', {'invisible': 0, 'layer': 'noplot'})
    assert ctx.resolve_visible(text) is True

    ctx = RenderContext(layout.doc, export_mode=True)
    text = layout.add_text('a', {'invisible': 0, 'layer': 'noplot'})
    assert ctx.resolve_visible(text) is False


def test_resolve_attrib_visibility():
    doc = ezdxf.new()
    layout = doc.modelspace()
    block = doc.blocks.new(name='block')
    doc.layers.new(name='invisible',
                   dxfattribs={'color': -1})  # color < 0 => invisible

    block.add_attdef('att1', (0, 0), '', {})
    block.add_attdef('att2', (0, 0), '', {'flags': const.ATTRIB_INVISIBLE})
    block.add_attdef('att3', (0, 0), '', {'layer': 'invisible'})

    i = layout.add_blockref('block', (0, 0))
    i.add_auto_attribs({'att1': 'abc', 'att2': 'def', 'att3': 'hij'})

    assert not i.attribs[0].is_invisible
    assert i.attribs[1].is_invisible
    assert not i.attribs[2].is_invisible

    ctx = RenderContext(layout.doc)
    assert ctx.resolve_visible(i.attribs[0]) is True
    assert ctx.resolve_visible(i.attribs[1]) is False
    assert ctx.resolve_visible(i.attribs[2]) is False


def test_resolve_entity_color(doc):
    ctx = RenderContext(doc)
    msp = doc.modelspace()
    lines = msp.query('LINE')
    line1 = ctx.resolve_all(lines[0])
    assert line1.color == '#0000ff'  # by layer

    line2 = ctx.resolve_all(lines[1])
    assert line2.color == '#ff0000'


def test_existing_true_color_overrides_any_aci_color(doc):
    ctx = RenderContext(doc)
    line = factory.new('LINE')
    line.rgb = (255, 1, 1)
    for color in range(const.BYLAYER + 1):
        line.dxf.color = color
        props = ctx.resolve_all(line)
        assert props.color == '#ff0101', \
            "true_color should override any ACI color"


def test_resolve_entity_linetype(doc):
    ctx = RenderContext(doc)
    msp = doc.modelspace()
    lines = msp.query('LINE')

    line1 = ctx.resolve_all(lines[0])
    assert line1.linetype_name == 'DOT'  # by layer

    line2 = ctx.resolve_all(lines[1])
    assert line2.linetype_name == 'DASHED'


def test_resolve_entity_lineweight(doc):
    ctx = RenderContext(doc)
    msp = doc.modelspace()
    lines = msp.query('LINE')

    line1 = ctx.resolve_all(lines[0])
    assert line1.lineweight == 0.70  # by layer

    line2 = ctx.resolve_all(lines[1])
    assert line2.lineweight == 0.50


def test_resolve_block_entities(doc):
    ctx = RenderContext(doc)
    msp = doc.modelspace()
    blockref = msp.query('INSERT').first
    ctx.push_state(ctx.resolve_all(blockref))
    assert ctx.inside_block_reference is True
    lines = list(blockref.virtual_entities())

    # properties by block
    line1 = ctx.resolve_all(lines[0])
    assert lines[0].dxf.linetype == 'BYBLOCK'
    assert line1.color == '#00ff00'
    assert line1.linetype_name == 'CENTER'
    assert line1.lineweight == 0.13

    # explicit properties
    line2 = ctx.resolve_all(lines[1])
    assert lines[1].dxf.linetype == 'DASHED'
    assert line2.color == '#ff0000'
    assert line2.linetype_name == 'DASHED'
    assert line2.lineweight == 0.50

    # properties by layer 'Test'
    line3 = ctx.resolve_all(lines[2])
    assert lines[2].dxf.linetype == 'BYLAYER'
    assert line3.color == '#0000ff'
    assert line3.linetype_name == 'DOT'
    assert line3.lineweight == 0.70

    ctx.pop_state()
    assert ctx.inside_block_reference is False


class TestResolveLayerACIColor7:
    @pytest.fixture
    def entity(self):
        # Default layer is '0' with default ACI color 7
        # Default entity color is BYLAYER
        return factory.new('LINE')

    @pytest.fixture(scope='class')
    def ctx(self):
        doc = ezdxf.new()
        doc.layers.new('TrueColor', dxfattribs={
            'true_color': ezdxf.rgb2int((0xB0, 0xB0, 0xB0))
        })
        context = RenderContext(doc)
        context.set_current_layout(doc.modelspace())
        return context

    def test_dark_background(self, ctx, entity):
        ctx.current_layout.set_colors(bg='#000000')
        assert ctx.resolve_color(entity).upper() == '#FFFFFF'

    def test_light_background(self, ctx, entity):
        ctx.current_layout.set_colors(bg='#FFFFFF')
        assert ctx.resolve_color(entity) == '#000000'

    def test_switch_layout_colors(self, ctx, entity):
        ctx.current_layout.set_colors(bg='#FFFFFF', fg='#A0A0A0')
        assert ctx.resolve_color(entity) == '#A0A0A0'
        ctx.current_layout.set_colors(bg='#EEEEEE', fg='#010101')
        assert ctx.resolve_color(entity) == '#010101'

    def test_color_from_true_color_layer(self, ctx, entity):
        entity.dxf.layer = 'TrueColor'
        assert ctx.resolve_color(entity).upper() == '#B0B0B0'

        # Entity ACI color is BYLAYER by default:
        assert entity.dxf.color == const.BYLAYER

        ctx.current_layout.set_colors(bg='#EEEEEE', fg='#010101')
        # But has no meaning if true color is set:
        assert ctx.resolve_color(entity).upper() == '#B0B0B0'


@pytest.mark.parametrize('color, result', [
    ('#012345', True),
    ('#456789', True),
    ('#ABCDEF', True),
    ('#abcdef', True),
    ('#ghijkl', False),
    ('000000', False),
    ('ABCDEF', False),
])
def test_is_valid_color(color, result):
    assert is_valid_color(color) is result


@pytest.mark.parametrize('color', [0, 1.0, (1, 2, 3)])
def test_invalid_color_value_type(color):
    with pytest.raises(TypeError):
        is_valid_color(color)


@pytest.mark.parametrize('color, result', [
    ('#00000000', True),
    ('#000000FF', True),
    ('#000000ff', True),
    ('#000000gh', False),
])
def test_is_valid_transparent_color(color, result):
    assert is_valid_color(color) is result


@pytest.mark.parametrize('color, result', [
    ('', False),
    ('#', False),
    ('#0', False),
    ('#00', False),
    ('#000', False),
    ('#0000', False),
    ('#00000', False),
    ('#000000', True),  # RGB color format
    ('#0000000', False),
    ('#00000000', True),  # RGB color format including alpha transparency
    ('#000000000', False),
    ('  #0000', False),
    ('  #000000', False),
])
def test_is_valid_color_value_length(color, result):
    assert is_valid_color(color) is result


if __name__ == '__main__':
    pytest.main([__file__])
