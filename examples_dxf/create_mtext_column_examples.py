# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf import zoom
from ezdxf.math import Vec3
from ezdxf.lldxf import const
from ezdxf.tools.text_layout import lorem_ipsum


def create_doc(filename: str, dxfversion: str):
    def add_mtext_columns(msp):
        insert = Vec3(0, 0, 0)
        attribs = {
            "layer": "STATIC",
            "char_height": 1,
            "insert": insert,
        }

        content = [
            " ".join(lorem_ipsum(50)),
            " ".join(lorem_ipsum(100)),
            " ".join(lorem_ipsum(70)),
        ]
        # Create 3 static columns, the content if each column is
        # clearly defined: [content0, content1, content2, ...]
        # The height of the columns is defined by their content, ezdxf adds
        # an automatic column switch `\N` (R2018) between the parts.
        # The height argument should as big as the tallest column needs to be,
        # this value also determines the total height of the MTEXT entity.
        #
        # This is the simplest way to define columns without the need to render
        # the content to determine the required column heights.
        mtext = msp.add_mtext_static_columns(
            content, width=20, gutter_width=1, height=100, dxfattribs=attribs
        )

        insert += Vec3(mtext.columns.total_width + 5, 0, 0)
        attribs["layer"] = "DYNAMIC"
        attribs["insert"] = insert
        content = " ".join(lorem_ipsum(300))

        # Create as much columns as needed for the given common fixed height:
        # Easy for R2018, very hard for <R2018
        # Passing count is required to calculate the correct total width.
        # The get the correct column count requires an exact MTEXT rendering
        # like AutoCAD/BricsCAD, which does not exist yet, but is planned for
        # the future.
        # DO NOT USE THIS INTERFACE IN PRODUCTION CODE!
        mtext = msp.add_mtext_dynamic_auto_height_columns(
            content,
            width=20,
            gutter_width=1,
            height=50,
            count=3,
            dxfattribs=attribs,
        )

        insert += Vec3(mtext.columns.total_width + 5, 0, 0)
        attribs["insert"] = insert

        # Create 3 columns with given individual column heights,
        # the last column height is required but ignored and therefore 0,
        # because the last column contains as much of the remaining content
        # as needed.
        # Easy for R2018, very hard for <R2018
        msp.add_mtext_dynamic_manual_height_columns(
            content,
            width=20,
            gutter_width=1,
            heights=[20, 30, 0],
            dxfattribs=attribs,
        )

    doc = ezdxf.new(dxfversion=dxfversion)
    msp = doc.modelspace()
    add_mtext_columns(msp)
    zoom.extents(msp)
    doc.saveas(filename)
    print(f"created {filename}")


if __name__ == "__main__":
    create_doc("mtext_columns_R2000.dxf", const.DXF2000)
    create_doc("mtext_columns_R2007.dxf", const.DXF2007)
    create_doc("mtext_columns_R2018.dxf", const.DXF2018)
