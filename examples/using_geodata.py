from pathlib import Path
from pprint import pprint
import ezdxf

# depends not included test files
DXF_TEST = Path(r'D:\Source\dxftest')
PRODUCTS = DXF_TEST / 'AutodeskProducts'

doc = ezdxf.readfile(PRODUCTS/'Map3D_2017.dxf')
msp = doc.modelspace()

for block_ref in msp.query("INSERT[layer=='VO_body+cisla']"):
    print('\nINSERT')
    pprint(block_ref.dxfattribs())
    # GEODATA handle is stored in the associated BLOCK_RECORD
    block_record = doc.block_records.get(block_ref.dxf.name)
    try:  # GEODATA handle is stored in an extension dictionary
        xdict = block_record.get_extension_dict()
    except ezdxf.DXFValueError:
        continue
    try:  # GEODATA handle is stored by key ACAD_GEOGRAPHICDATA
        geodata_handle = xdict['ACAD_GEOGRAPHICDATA']
    except ezdxf.DXFKeyError:
        pass
    else:  # but this seems never the case for a block reference
        print('uses GEODATA(#{})'.format(geodata_handle))

# GEODATA entity is only referenced by the model space
geodata = msp.get_geodata()
print("\nNEW NEW NEW!")
print('Model space uses: ' + str(geodata))
pprint(geodata.dxfattribs())
print(geodata.coordinate_system_definition)
print(str(geodata.source_vertices))
print(str(geodata.target_vertices))
pprint(geodata.faces, width=160)
