# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
from __future__ import annotations

import ezdxf
from ezdxf.entities import Dictionary, DXFEntity

EX1 = r"C:\Source\dxftest\ACAD_R2010.dxf"
EX2 = r"C:\Source\dxftest\AutodeskSamples\title_block-iso.dxf"
ISSUE_1203 = r"C:\Users\mozman\Desktop\Now\ezdxf\1203\dynblock.dxf"
ISSUE_1279 = r"C:\Users\mozman\Desktop\Now\ezdxf\1279\1279_orig.dxf"
ISSUE_1285 = r"C:\Users\mozman\Desktop\Now\ezdxf\1285\add_clipping_path_in_block_coordinates.dxf"

"""
Analyze DICTIONARY
==================

GOAL: What is the default state of the "hard-owned" flag - group code 280.

DXF Reference 2018:

   280 - Hard-owner flag.
   If set to 1, indicates that elements of the dictionary are to be treated as
   hard-owned

No definition of the default state in the DXF reference!

AutoCAD R2010
-------------

Example File: ACAD_R2010.dxf

    1. The root-dict doesn't have the flag.
    2. The entries in the root-dict don't have the flag.
    3. Extension-dicts do have the flag and the value is set to 1
    
    Conclusion: default value of the hard-owned flag is 0

AutoCAD R2018
-------------

Example File: title_block-iso.dxf

    1. The root-dict doesn't have the flag.
    2. The entries in the root-dict don't have the flag.
    
Undocumented extension dict of the INSERT(#1E98) entity:

    DICTIONARY(#2020): has-hard-owned-flag: True; state: 1
        owner: INSERT(#1E98); is-extension-dict: True
        owner-dict-key: not a dict-entry
    
    Contains the following dict by key 'AcDbBlockRepresentation'
            
    DICTIONARY(#2021): has-hard-owned-flag: True; state: 1
        owner: DICTIONARY(#2020); is-extension-dict: False
        owner-dict-key: AcDbBlockRepresentation
        
    Contains the following dict by key 'AppDataCache'
    
    DICTIONARY(#2023): has-hard-owned-flag: True; state: 1
        owner: DICTIONARY(#2021); is-extension-dict: False
        owner-dict-key: AppDataCache

    Contains the following dict by key 'ACAD_ENHANCEDBLOCKDATA'

    DICTIONARY(#22D5): has-hard-owned-flag: True; state: 1
        owner: DICTIONARY(#2023); is-extension-dict: False
        owner-dict-key: ACAD_ENHANCEDBLOCKDATA

    3. Extension-dicts and contained dictionaries do have the flag and the value is set to 1
    

Current implementation of ezdxf for new DXF files
-------------------------------------------------

    1. The root-dict does have the flag and the state is 0.
    2. The entries in the root-dict have the flag and the state is 0.
    3. Extension-dicts do have the flag and the value is set to 1
    
    Conclusion: the state is correct, but the flag doesn't have to be present if the 
    state is 0.
 
Related issues:
---------------

    - #1203: Copying dynamic blocks via clipboard removes dynamic features
    - #1276: Copy to clipboard failed issue found from version 1.3.5 (no example file)
    - #1279: ezdxf audit does not repair the drawing (crash on ctrl+c)
    - #1285: Copying clipped blocks via clipboard removes clipping

Tests:
------

    - test suite works without errors: YES
    - new DXF files can be opened in BricsCAD: YES
        - tested R2000, R2004, R2007, R2010, R2013, R2018 
        - AUDIT command reports 0 errors
    - new DXF files can be opened in AutoCAD (DWG TrueView): YES
        - tested R2000, R2004, R2007, R2010, R2013, R2018
        - DWG TrueView cannot audit DXF files
    - new DXF file - copy/paste of entities works in BricsCAD: YES
        - tested R2000, R2004, R2007, R2010, R2013, R2018
    - copy/paste #1203 works in BricsCAD: YES
        - copy/paste works and dynamic feature L1 is preserved
    - copy/paste #1279 works in BricsCAD: NO
        - BricsCAD crashes
    - auditor repairs #1279: NO
        - BricsCAD crashes on copy/paste
    - copy/paste #1285 - copy/paste of clipped INSERT works in BricsCAD: YES
        - clipping path is preserved

"""

CLONING = {
    0: "not applicable",
    1: "keep existing",
    2: "use clone",
    3: "<xref>$0$<name>",
    4: "$0$<name>",
    5: "Unmangle name",
}

def is_ext_dict(d: Dictionary, owner: DXFEntity) -> bool:
    if owner and owner.has_extension_dict:
        ext_dict = owner.extension_dict
        return ext_dict.dictionary is d
    return False


def get_dict_name(d: Dictionary, owner: DXFEntity) -> str:
    if owner and isinstance(owner, Dictionary):
        return owner.find_key(d)
    return "not a dict-entry"


def print_dict_info(d: Dictionary) -> None:
    entitydb = d.doc.entitydb
    owner = entitydb.get(d.dxf.owner)
    has_hard_owner_flag = d.dxf.hasattr("hard_owned")
    has_cloning_flag = d.dxf.hasattr("cloning")
    state = d.dxf.hard_owned
    cloning = d.dxf.cloning
    print(f"\n{d}")
    print(f"    owner: {owner}")
    print(f"    is extension-dict: {is_ext_dict(d, owner)}")
    print(f"    owner dict-key: {get_dict_name(d, owner)}")
    print(f"    has hard-owned flag: {has_hard_owner_flag}")
    print(f"        state: {state}")
    print(f"    has cloning flag: {has_cloning_flag}")
    print(f"        state: {cloning} - {CLONING.get(cloning)}")


def main(filename: str):
    doc = ezdxf.readfile(filename)
    dicts = doc.entitydb.query("DICTIONARY")
    for d in dicts:
        print_dict_info(d)

    print(f"\nfound {len(dicts)} DICTIONARY entities.")


def new_doc():
    doc = ezdxf.new()
    msp = doc.modelspace()
    line = msp.add_line((0, 0), (1, 0))
    ext_dict = line.new_extension_dict()

    dicts = doc.entitydb.query("DICTIONARY")
    for d in dicts:
        print_dict_info(d)

    print(f"found {len(dicts)} DICTIONARY entities.")


if __name__ == "__main__":
    # new_doc()
    main(ISSUE_1285)
