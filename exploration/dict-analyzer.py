# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
from __future__ import annotations

import ezdxf
from ezdxf.entities import Dictionary, DXFEntity

EX1 = r"C:\Source\dxftest\ACAD_R2010.dxf"
EX2 = r"C:\Source\dxftest\AutodeskSamples\title_block-iso.dxf"
ISSUE_1203 = r"C:\Users\mozman\Desktop\Now\ezdxf\1203\dynblock.dxf"
ISSUE_1279 = r"C:\Users\mozman\Desktop\Now\ezdxf\1279\1279_orig.dxf"

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
    - new DXF file - copy/paste of clipped INSERT works in BricsCAD: YES/NO
        - copy/paste works, but clipping is removed
    - copy/paste #1203 works in BricsCAD: YES
        - copy/paste works and dynamic feature L1 is preserved
    - copy/paste #1279 works in BricsCAD: NO
        - BricsCAD crashes
    - auditor fixes #1279: NO
        - BricsCAD crashes on copy/paste
"""


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

    state = "unknown"
    has_hard_owner_flag = d.dxf.hasattr("hard_owned")
    if has_hard_owner_flag:
        state = str(d.dxf.hard_owned)
    print(f"{d}: has-hard-owned-flag: {has_hard_owner_flag}; state: {state}")
    print(f"    owner: {owner}; is-extension-dict: {is_ext_dict(d, owner)}")
    key_name = get_dict_name(d, owner)
    if key_name:
        print(f"    owner-dict-key: {key_name}")


def main(filename: str):
    doc = ezdxf.readfile(filename)
    dicts = doc.entitydb.query("DICTIONARY")
    for d in dicts:
        print_dict_info(d)

    print(f"found {len(dicts)} DICTIONARY entities.")


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
    main(ISSUE_1203)
