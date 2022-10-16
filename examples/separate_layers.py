#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import Importer
from ezdxf.query import EntityQuery

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

SOURCE_DXF = "test.dxf"

# ------------------------------------------------------------------------------
# This example shows how to separate entities by their layer attribute
#
# The example imports all entities from the modelspace into a new DXF document.
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
    source_doc = ezdxf.readfile(CWD / SOURCE_DXF)
    source_msp = source_doc.modelspace()
    # create an EntityQuery container with all entities from the modelspace
    source_entities = source_msp.query()
    # get all layer names from entities in the modelspace:
    all_layer_names = [e.dxf.layer for e in source_entities]
    # remove unwanted layers if needed

    for layer_name in all_layer_names:
        # create a new document for each layer with the same DXF version as the
        # source file
        layer_doc = ezdxf.new(dxfversion=source_doc.dxfversion)
        layer_msp = layer_doc.modelspace()
        importer = Importer(source_doc, layer_doc)
        # select all entities from modelspace from this layer (extended query
        # feature of class EntityQuery)
        entities: EntityQuery = source_entities.layer == layer_name  # type: ignore
        if len(entities):
            importer.import_entities(entities, layer_msp)
            # create required resources
            importer.finalize()
            layer_doc.saveas(CWD / f"{layer_name}.dxf")


if __name__ == "__main__":
    main()
