#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf.types import dxftag

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def add_graphic_entity_to_root_dict(doc: Drawing):
    msp = doc.modelspace()
    line = msp.add_line((0, 0), (1, 0))
    # Question: is it possible to store graphical entities which reside in a
    # layout in the root dictionary (Autodesk term: the named dictionary)
    # doc.rootdict["LINE"] = line  # this does not work for v0.17 as consequence!
    # HACK HACK HACK!!! - DO NOT USE HANDLES IN PRODUCTION CODE!
    doc.rootdict["LINE"] = line.dxf.handle
    # BricsCAD opens the file but AUDIT complaints:
    # Name: AcDbDictionary(A)
    # Value: Duplicate ownership of reference (2F)
    # Validation: Invalid
    # Default value: Removed
    # TrueView 2021 opens the file - AUDIT command is not available
    #
    # "2F" is the handle of the LINE entity.
    # The error message means the LINE entity can only have one owner and that
    # is the layout the entity resides in. A dictionary is also the owner of its
    # entries, which leads to conflict shown above.
    #
    # Consequence: ezdxf v0.17 can not add graphical entities to dictionaries


def reference_graphic_entities_in_extension_dictionaries(doc):
    # The extension dictionary is a DICTIONARY object and cannot reference
    # directly graphical entities (see function add_graphic_entity_to_root_dict()).
    # A XRECORD object is not a graphical entity and can store arbitrary data
    # and is therefore a good choice to attach data to a graphical entity by an
    # extension dictionary.

    msp = doc.modelspace()
    line = msp.add_line((0, 0), (1, 0))
    line1 = msp.add_line((0, 1), (1, 1))
    line2 = msp.add_line((0, 2), (1, 2))
    # Attach references to line1 and line2 to the line entity:
    ext_dict = line.new_extension_dict()
    xrecord = ext_dict.add_xrecord("LINK_CONTAINER")
    # The group code 360 is used in DICTIONARY to store handles to linked
    # objects and seems to be a good choice:
    xrecord.tags.append(dxftag(360, line1.dxf.handle))
    xrecord.tags.append(dxftag(360, line2.dxf.handle))


def main():
    doc = ezdxf.new()
    add_graphic_entity_to_root_dict(doc)
    reference_graphic_entities_in_extension_dictionaries(doc)
    doc.saveas(CWD / "dictionary.dxf")


if __name__ == "__main__":
    main()
