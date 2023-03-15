#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pathlib
import ezdxf
from ezdxf.document import Drawing
from ezdxf import xref, units

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to load DXF resources from the TABLES section by the
# xref module from one DXF document into another DXF document.
# ------------------------------------------------------------------------------


def make_source_document(dxfversion="R2013") -> Drawing:
    doc = ezdxf.new(dxfversion, units=units.M, setup=True)
    doc.linetypes.add(
        "GAS",
        pattern='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
        description="Gas ----GAS----GAS----GAS----GAS----GAS----GAS--",
        length=1,
    )
    doc.layers.add("Layer0", color=1, linetype="GAS")
    return doc


def load_resources(source_doc: Drawing, target_doc: Drawing) -> None:
    loader = xref.Loader(source_doc, target_doc)

    # Load all layers:
    # The default layers "0" and "DEFPOINTS" will not be loaded, they always exist
    # in the target document!
    loader.load_layers([layer.dxf.name for layer in source_doc.layers])

    # Load specific linetypes:
    # The linetype "GAS" will be loaded automatically, because it's used by layer
    # "Layer0", adding "GAS" to the linetypes to load does no harm, but it's not
    # necessary.
    loader.load_linetypes(["CENTER", "DASHED", "DASHDOT"])

    # Load specific text style:
    loader.load_text_styles(["OpenSans", "LiberationMono"])

    # Load all DIMENSION styles, loads also the dependent text style
    # "OpenSansCondensed-Light":
    loader.load_dim_styles([dimstyle.dxf.name for dimstyle in source_doc.dimstyles])

    # start loading process:
    loader.execute()

    # There are also loading methods for:
    # - MATERIAL: load_materials()
    # - MLINESTYLE: load_mline_styles()
    # - MLEADERSTYLE: load_mleader_styles()


def main():
    dxfversion = "R2013"
    source_doc = make_source_document(dxfversion)
    target_doc = ezdxf.new(dxfversion)
    load_resources(source_doc, target_doc)
    target_doc.saveas(CWD / "loaded_table_resource.dxf")


if __name__ == "__main__":
    main()
