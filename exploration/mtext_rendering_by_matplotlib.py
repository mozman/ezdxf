#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import List
import pathlib
import ezdxf
from ezdxf.math import Vec2
from ezdxf.tools.text_size import mtext_size, WordSizeDetector
from ezdxf import path, colors
from ezdxf.addons import text2path
from ezdxf.addons import MTextExplode

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def rect(p1: Vec2, p2: Vec2) -> List[Vec2]:
    return [
        p1,
        Vec2(p2.x, p1.y),
        p2,
        Vec2(p1.x, p2.y),
    ]


def main():
    doc = ezdxf.new()
    doc.styles.add("ARIAL", font="arial.ttf")
    box_layer = doc.layers.add(
        "bounding boxes based on Matplotlib", color=colors.MAGENTA
    )
    mtext_layer = doc.layers.add("MTEXT by current viewer")
    path_layer = doc.layers.add(
        "path rendering by Matplotlib", color=colors.YELLOW
    )

    msp = doc.modelspace()
    mtext = msp.add_mtext(
        "111111\n22222\n3333",
        dxfattribs={"style": "ARIAL", "layer": mtext_layer.dxf.name},
    )
    print(f"MTEXT width: {mtext.dxf.width}")
    print(f"MTEXT cap height: {mtext.dxf.char_height}")

    # Add bounding boxes for all words:
    word_size_detector = WordSizeDetector()
    size = mtext_size(mtext, tool=word_size_detector)
    for p1, p2 in word_size_detector.word_boxes():
        msp.add_lwpolyline(
            rect(p1, p2), close=True, dxfattribs={"layer": box_layer.dxf.name}
        )

    # Add bounding boxes for whole MTEXT entity:
    msp.add_lwpolyline(
        rect(Vec2(0, -size.total_height), Vec2(size.total_width, 0)),
        close=True,
        dxfattribs={"layer": box_layer.dxf.name},
    )

    # Add path renderings done by Matplotlib::
    with MTextExplode(msp) as mtxpl:
        mtxpl.explode(mtext, destroy=False)

    for text_entity in msp.query("TEXT"):
        text_path = text2path.make_path_from_entity(text_entity)
        path.render_lwpolylines(
            msp,
            [text_path],
            dxfattribs={
                "layer": path_layer.dxf.name,
            },
        )
        text_entity.destroy()

    doc.set_modelspace_vport(
        size.total_height * 1.1,
        center=(size.total_width / 2, -size.total_height / 2),
    )
    doc.saveas(CWD / "mtext_rendering_by_matplotlib.dxf")


if __name__ == "__main__":
    main()
