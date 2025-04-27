# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
#
# Fixes ownership issues of DICTIONARY entities like in #1279.
#
from ezdxf import recover, DXFStructureError
from ezdxf.entities import Dictionary, DXFEntity

DXF_FILE = "your.dxf"
RECOVER_FILE = "recover.dxf"


def is_ext_dict(d: Dictionary, owner: DXFEntity) -> bool:
    if owner and owner.has_extension_dict:
        ext_dict = owner.extension_dict
        return ext_dict.dictionary is d
    return False


def main(filename: str, recover_file: str):
    try:
        doc, auditor = recover.readfile(filename)
    except DXFStructureError as e:
        print(f"{e} in file {filename}.")
        return
    except IOError as e:
        print(str(e))
        return

    entitydb = doc.entitydb
    for d in doc.entitydb.query("DICTIONARY"):
        owner = entitydb.get(d.dxf.owner)
        d.dxf.hard_owned = 1 if is_ext_dict(d, owner) else 0

    doc.saveas(recover_file)


if __name__ == "__main__":
    main(DXF_FILE, RECOVER_FILE)
