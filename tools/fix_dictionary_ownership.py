# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
#
# Fixes ownership issues of DICTIONARY entities like in #1279.
#
from ezdxf import recover, DXFStructureError
from ezdxf.version import version
from ezdxf.entities import Dictionary

DXF_FILE = "your.dxf"
RECOVER_FILE = "recover.dxf"


def patch_dictionary_hard_owned_flag():
    hard_owned = Dictionary.DXFATTRIBS.get("hard_owned")
    hard_owned.default = 0


def set_ownership_recursive(d: Dictionary, *, flag: int) -> None:
    assert isinstance(d, Dictionary) is True
    d.dxf.hard_owned = flag
    for _, entity in d.items():
        if isinstance(entity, Dictionary):
            set_ownership_recursive(entity, flag=flag)


def main(filename: str, recover_file: str):
    try:
        doc, _ = recover.readfile(filename)
    except DXFStructureError as e:
        print(f"{e} in file {filename}.")
        return
    except IOError as e:
        print(str(e))
        return

    if version[:3] < (1, 4, 2):  # patch older versions of ezdxf
        patch_dictionary_hard_owned_flag()

    # set hard-owned-flag of the rootdict to 0
    set_ownership_recursive(doc.rootdict, flag=0)

    # set hard-owned-flag of extension dicts to 1
    for entity in doc.modelspace():
        if not entity.has_extension_dict:
            continue
        xdict = entity.get_extension_dict()
        set_ownership_recursive(xdict.dictionary, flag=1)

    doc.saveas(recover_file)


if __name__ == "__main__":
    main(DXF_FILE, RECOVER_FILE)
