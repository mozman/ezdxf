#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf.math import Vec3

TRANSPARENCIES = [
    None,  # ByLayer
    ezdxf.const.TRANSPARENCY_BYBLOCK,
    ezdxf.float2transparency(0.0),
    ezdxf.float2transparency(0.3),
    ezdxf.float2transparency(0.6),
    ezdxf.float2transparency(0.9),
    ezdxf.float2transparency(1.0),
]
SIZE = 2.0
FILL_COLOR = ezdxf.const.RED
BACKGROUND_COLOR = ezdxf.const.BLUE
ARIAL = "ARIAL"
TEXT_HEIGHT = 0.4
BG_WIDTH = 60
BG_HEIGHT = 30


def transparency_to_text(value: int) -> str:
    if value == ezdxf.const.TRANSPARENCY_BYBLOCK:
        return "BYBLOCK"
    elif value is None:
        return "BYLAYER"
    return f"{ezdxf.transparency2float(value):.2f}"


def style(height=1.0, style=ARIAL, layer="TEXT"):
    return {"style": style, "height": height, "layer": layer}


def create_fields(layout, pos: Vec3, layer="0"):
    for index, transparency in enumerate(TRANSPARENCIES):
        dxfattribs = {
            "color": FILL_COLOR,
            "layer": layer,
        }

        if transparency is not None:
            dxfattribs["transparency"] = transparency

        y = index * SIZE * 2
        location = pos + Vec3(0, y, 0)
        layout.add_solid(
            [
                location,
                location + (SIZE, 0),
                location + (0, SIZE),
                location + (SIZE, SIZE),
            ],
            dxfattribs=dxfattribs,
        )
        layout.add_text(
            transparency_to_text(transparency),
            dxfattribs=style(TEXT_HEIGHT),
        ).set_pos(location - (0, TEXT_HEIGHT * 1.5))


def main(filename: str):
    doc = ezdxf.new()
    doc.styles.add(ARIAL, font="arial.ttf")
    doc.layers.add("TEXT")
    doc.layers.add("LAY_T50", transparency=0.5)

    msp = doc.modelspace()
    msp.add_solid(
        [(0, 0), (BG_WIDTH, 0), (0, BG_HEIGHT), (BG_WIDTH, BG_HEIGHT)],
        dxfattribs={"color": BACKGROUND_COLOR},
    )
    # modelspace fields on layer "0"
    pos = Vec3(2, 1, 0)
    msp.add_text("MSP", dxfattribs=style(0.7)).set_pos(pos)
    create_fields(msp, pos + (0, 2), layer="0")

    # modelspace fields on layer "LAY_T50"
    pos = Vec3(8, 1, 0)
    msp.add_text("LAYER 50%", dxfattribs=style(0.7)).set_pos(pos)
    create_fields(msp, pos + (0, 2), layer="LAY_T50")

    doc.set_modelspace_vport(BG_HEIGHT, (BG_HEIGHT / 2, BG_HEIGHT / 2))
    doc.saveas(filename)


if __name__ == "__main__":
    main("transparency_checker.dxf")
