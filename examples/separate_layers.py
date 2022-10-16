#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import Importer
from ezdxf.entities import DXFEntity

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

SOURCE_DXF = "test.dxf"

# ------------------------------------------------------------------------------
# This example shows how to separate entities by their layer attribute
#
# The example imports all entities from each layer defined in the layer table
# into a new DXF document. The catch: a layer don't have to have an entry in the
# layer table!
# The Importer add-on is required to also import the required resources used by
# the imported entities.
#
# Important advice:
# Keep things simple, more complex DXF documents may fail or at least the entities
# will not look the same as in the source file! Read the docs!
#
# Basic concept of layers : https://ezdxf.mozman.at/docs/concepts/layers.html
# Importer add-on: https://ezdxf.mozman.at/docs/addons/index.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.readfile(CWD / SOURCE_DXF)
    msp = doc.modelspace()
    # create an EntityQuery container with all entities from the modelspace
    all_entities = msp.query()
    # get all existing layers, filter unwanted layers if needed
    all_layer_names = [layer.dxf.name for layer in doc.layers]
    for layer_name in all_layer_names:
        # create a new document for each layer and the same DXF version as the
        # source file
        layer_doc = ezdxf.new(dxfversion=doc.dxfversion)
        layer_msp = layer_doc.modelspace()
        importer = Importer(doc, layer_doc)
        # select all entities from modelspace from this layer
        entities: list[DXFEntity] = all_entities.layer == layer_name  # type: ignore
        if len(entities):
            importer.import_entities(entities, layer_msp)
        # create required resources
        importer.finalize()
        layer_doc.saveas(CWD / f"{layer_name}.dxf")


if __name__ == "__main__":
    main()
