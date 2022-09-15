# Copyright (c) 2018-2022 Manfred Moitzi
# License: MIT License
from pprint import pprint
import ezdxf

# depends on a not included test files
PRODUCTS = ezdxf.options.test_files_path / "AutodeskProducts"

doc = ezdxf.readfile(PRODUCTS / "Map3D_2017.dxf")
msp = doc.modelspace()

for block_ref in msp.query("INSERT[layer=='VO_body+cisla']"):
    print("\nINSERT")
    pprint(block_ref.dxfattribs())
    # GEODATA handle is stored in the associated BLOCK_RECORD
    block_record = doc.block_records.get(block_ref.dxf.name)

    # GEODATA handle is stored in an extension dictionary
    if block_record.has_extension_dict:
        xdict = block_record.get_extension_dict()
    else:
        continue
    try:  # GEODATA handle is stored by key ACAD_GEOGRAPHICDATA
        geodata_handle = xdict["ACAD_GEOGRAPHICDATA"]
    except ezdxf.DXFKeyError:
        pass
    else:  # but this seems never the case for a block reference
        print(f"uses GEODATA(#{geodata_handle})")

# GEODATA entity is only referenced by the modelspace
geodata = msp.get_geodata()
print("\nNEW NEW NEW!")
print("Modelspace uses: " + str(geodata))
pprint(geodata.dxfattribs())
print(geodata.coordinate_system_definition)
print(str(geodata.source_vertices))
print(str(geodata.target_vertices))
pprint(geodata.faces, width=160)
