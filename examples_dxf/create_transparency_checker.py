#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Optional, List, Tuple
import ezdxf
from ezdxf import colors
from ezdxf.math import Vec3

EXPLICIT_TRANSPARENCIES = [0.2, 0.4, 0.6, 0.8]
SIZE = 2.0
FILL_COLOR = colors.RED
BACKGROUND_COLOR = colors.BLUE
ARIAL = "ARIAL"
TEXT_HEIGHT = 0.25
BG_WIDTH = 38
BG_HEIGHT = 20

MULTI_BLK = "MULTI_BLK"
BYLAYER_BLK = "BYLAYER_BLK"
BYBLOCK_BLK = "BYBLOCK_BLK"

MULTI_BLK_T50 = "MULTI_BLK_T50"
BYLAYER_BLK_T50 = "BYLAYER_BLK_T50"
BYBLOCK_BLK_T50 = "BYBLOCK_BLK_T50"


def solid_vertices(location: Vec3, width: float, height: float) -> List[Vec3]:
    vertices = rect(location, width, height)
    vertices[2], vertices[3] = vertices[3], vertices[2]
    return vertices


def rect(location: Vec3, width: float, height: float) -> List[Vec3]:
    return [
        location,
        location + (width, 0),
        location + (width, height),
        location + (0, height),
    ]


def add_solid_field(
    layout, location: Vec3, transparency: Optional[int], *, size=SIZE, layer="0"
):
    dxfattribs = {
        "color": FILL_COLOR,
        "layer": layer,
    }

    if transparency is not None:
        dxfattribs["transparency"] = transparency

    layout.add_solid(
        solid_vertices(location, size, size),
        dxfattribs=dxfattribs,
    )
    add_frame(layout, location, size, size)


def add_multi_field(
    layout,
    location: Vec3,
    values: List[float],
    color=FILL_COLOR,
    *,
    size=1.0,
    layer="0",
):
    # make n strips with explicit transparency values
    width = size / len(values)
    height = size
    offset = Vec3(width, 0)
    pos = location
    for transparency in values:
        layout.add_solid(
            solid_vertices(pos, width, height),
            dxfattribs={
                "color": color,
                "layer": layer,
                "transparency": colors.float2transparency(transparency),
            },
        )
        pos += offset
    add_frame(layout, location, size, size)


def add_mtext(
    layout,
    text: str,
    location: Vec3,
    height: float,
    layer="TEXT",
):
    layout.add_mtext(
        text,
        dxfattribs={
            "style": ARIAL,
            "char_height": height,
            "layer": layer,
        },
    ).set_location(location, attachment_point=ezdxf.const.MTEXT_TOP_LEFT)


def add_frame(
    layout,
    location: Vec3,
    width: float,
    height: float,
    color: int = colors.WHITE,
    layer: str = "0",
):
    layout.add_lwpolyline(
        rect(location, width, height),
        close=True,
        dxfattribs={
            "color": color,
            "layer": layer,
        },
    )


def add_fields(layout, location: Vec3, layer: str = "0"):
    size = SIZE
    text_height = size / 8.0
    offset = Vec3(0, size * 2)
    text_offset = Vec3(text_height * 0.5, text_height * 1.5)
    pos = location
    for transparency, name in [
        (None, "BYLAYER"),
        (colors.TRANSPARENCY_BYBLOCK, "BYBLOCK"),
        (EXPLICIT_TRANSPARENCIES, "EXPLICIT"),
    ]:
        if isinstance(transparency, list):
            add_multi_field(
                layout,
                pos,
                EXPLICIT_TRANSPARENCIES,
                size=size,
                layer=layer,
            )
        else:
            add_solid_field(
                layout,
                pos,
                transparency,
                size=size,
                layer=layer,
            )
        add_mtext(layout, name, pos + text_offset, text_height)
        pos += offset


def add_blocks(
    layout, location: Vec3, names: List[Tuple[str, str]], layer: str = "0"
):
    size = SIZE
    text_height = size / 8.0
    text_offset = Vec3(text_height * 0.5, text_height * 1.5)
    offset = Vec3(0, size * 2)
    pos = location
    for name, text in names:
        insert = layout.add_blockref(name, pos)
        insert.dxf.layer = layer
        insert.set_scale(size)
        add_mtext(layout, text, pos + text_offset, text_height)
        pos += offset


def make_multi_block(
    doc, name: str, values: List[float], color=FILL_COLOR, size=1.0, layer="0"
):
    # make n strips with explicit transparency values
    multi_blk = doc.blocks.new(name)
    add_multi_field(
        multi_blk, Vec3(0, 0), values, color, size=size, layer=layer
    )


def make_single_block(
    doc,
    name: str,
    transparency: Optional[int],
    color=FILL_COLOR,
    size=1.0,
    layer="0",
):
    bylayer_blk = doc.blocks.new(name)
    location = Vec3(0, 0)
    attribs = {
        "color": color,
        "layer": layer,
    }
    if transparency is not None:
        attribs["transparency"] = transparency

    bylayer_blk.add_solid(
        solid_vertices(location, size, size),
        dxfattribs=attribs,
    )
    add_frame(bylayer_blk, location, size, size)


def main(filename: str):
    doc = ezdxf.new()
    doc.styles.add(ARIAL, font="arial.ttf")
    doc.layers.add("TEXT")
    layer_bg = doc.layers.add("BACKGROUND")
    layer_bg.lock()
    layer_t50 = doc.layers.add("T50", transparency=0.5)
    layer_t50_name = layer_t50.dxf.name
    layer_t80 = doc.layers.add("T80", transparency=0.80)
    layer_t80_name = layer_t80.dxf.name

    # SOLIDS on layer "0"
    make_multi_block(doc, MULTI_BLK, EXPLICIT_TRANSPARENCIES)
    make_single_block(doc, BYLAYER_BLK, None)
    make_single_block(doc, BYBLOCK_BLK, colors.TRANSPARENCY_BYBLOCK)

    # SOLIDS on layer "T50"
    make_multi_block(
        doc, MULTI_BLK_T50, EXPLICIT_TRANSPARENCIES, layer=layer_t50_name
    )
    make_single_block(doc, BYLAYER_BLK_T50, None, layer=layer_t50_name)
    make_single_block(
        doc, BYBLOCK_BLK_T50, colors.TRANSPARENCY_BYBLOCK, layer=layer_t50_name
    )

    msp = doc.modelspace()

    # add background filling
    msp.add_solid(
        [(0, 0), (BG_WIDTH, 0), (0, BG_HEIGHT), (BG_WIDTH, BG_HEIGHT)],
        dxfattribs={
            "color": BACKGROUND_COLOR,
            "layer": layer_bg.dxf.name,
        },
    )

    # modelspace fields on layer "0"
    text_top_y = 3.5
    column_x = 2.0
    height = 0.35
    gap = 1.5
    pos = Vec3(column_x, text_top_y, 0)
    add_mtext(msp, "model space\nSOLID layer: '0'", pos, height=height)
    add_fields(msp, pos + (0, gap), layer="0")

    # modelspace fields on layer "LAY_T50"
    column_x += 6
    pos = Vec3(column_x, text_top_y, 0)
    add_mtext(
        msp,
        f"model space\nSOLID layer: '{layer_t50_name}'",
        pos,
        height=height,
    )
    add_fields(msp, pos + (0, gap), layer=layer_t50_name)

    # blocks on layer "0", SOLIDS on layer "0"
    column_x += 6
    pos = Vec3(column_x, text_top_y, 0)
    add_mtext(
        msp,
        "block references\n"
        "INSERT layer: '0'\n"
        "SOLID layer: '0'",
        pos,
        height=height,
    )
    add_blocks(
        msp,
        pos + (0, gap),
        [
            (BYLAYER_BLK, "BYLAYER"),
            (BYBLOCK_BLK, "BYBLOCK"),
            (MULTI_BLK, "EXPLICIT"),
        ],
        layer="0",
    )

    # blocks on layer "T50", SOLIDS on layer "0"
    column_x += 6
    pos = Vec3(column_x, text_top_y, 0)
    add_mtext(
        msp,
        f"block references\n"
        f"INSERT layer: '{layer_t50_name}'\n"
        f"SOLID layer: '0'",
        pos,
        height=height,
    )
    add_blocks(
        msp,
        pos + (0, gap),
        [
            (BYLAYER_BLK, "BYLAYER"),
            (BYBLOCK_BLK, "BYBLOCK"),
            (MULTI_BLK, "EXPLICIT"),
        ],
        layer=layer_t50_name,
    )

    # blocks on layer "0", SOLIDS on layer "T50"
    column_x += 6
    pos = Vec3(column_x, text_top_y, 0)
    add_mtext(
        msp,
        f"block references\n"
        f"INSERT layer: '0'\n"
        f"SOLID layer: '{layer_t50_name}'",
        pos,
        height=height,
    )
    add_blocks(
        msp,
        pos + (0, gap),
        [
            (BYLAYER_BLK_T50, "BYLAYER"),
            (BYBLOCK_BLK_T50, "BYBLOCK"),
            (MULTI_BLK_T50, "EXPLICIT"),
        ],
        layer="0",
    )

    # blocks on layer "T80", SOLIDS on layer "T50"
    column_x += 6
    pos = Vec3(column_x, text_top_y, 0)
    add_mtext(
        msp,
        f"block references\nINSERT layer: '{layer_t80_name}'\n"
        f"SOLID layer: '{layer_t50_name}'",
        pos,
        height=height,
    )
    add_blocks(
        msp,
        pos + (0, gap),
        [
            (BYLAYER_BLK_T50, "BYLAYER"),
            (BYBLOCK_BLK_T50, "BYBLOCK"),
            (MULTI_BLK_T50, "EXPLICIT"),
        ],
        layer=layer_t80_name,
    )
    add_mtext(
        msp,
        "EXPLICT: SOLID transparency as explicit value\n"
        "BYBLOCK: SOLID transparency inherited from INSERT\n"
        "BYLAYER: SOLID transparency inherited from layer",
        Vec3(2, 18),
        height=height,
    )

    doc.set_modelspace_vport(
        max(BG_HEIGHT, BG_WIDTH), (BG_HEIGHT / 2, BG_HEIGHT / 2)
    )
    doc.saveas(filename)


if __name__ == "__main__":
    main("transparency_checker.dxf")
