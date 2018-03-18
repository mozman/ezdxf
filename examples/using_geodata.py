from pathlib import Path
from pprint import pprint
import ezdxf

# depends not included test files
DXF_TEST = Path(r'D:\Source\dxftest')
PRODUCTS = DXF_TEST / 'AutodeskProducts'

dwg = ezdxf.readfile(PRODUCTS/'Map3D_2017.dxf')
msp = dwg.modelspace()

for block_ref in msp.query("INSERT[layer=='VO_body+cisla']"):
    print('\nINSERT')
    pprint(block_ref.dxfattribs())
    # GEODATA handle is stored in the associated BLOCK_RECORD
    block_record = dwg.block_records.get(block_ref.dxf.name)
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
if hasattr(msp, 'get_geodata'):
    # NEW 18.03.2018
    geodata = msp.get_geodata()
    print("\nNEW NEW NEW!")
    print('Model space uses: ' + str(geodata))
    pprint(geodata.dxfattribs())
    print(geodata.get_coordinate_system_definition())

else:
    try:  # GEODATA handle is stored in an extension dictionary
        # layouts store their associated BLOCK_RECORD
        xdict = msp.block_record.get_extension_dict()
    except ezdxf.DXFValueError:
        pass
    else:
        try:  # GEODATA handle is stored by key ACAD_GEOGRAPHICDATA
            geodata_handle = xdict['ACAD_GEOGRAPHICDATA']
        except ezdxf.DXFKeyError:
            pass
        else:
            print('Model space uses GEODATA(#{})'.format(geodata_handle))
            geodata = dwg.get_dxf_entity(geodata_handle)
            pprint(geodata.dxfattribs())

    # Or you can query all GEODATA entities in the objects section
    # because all GEODATA objects know their host BLOCK_RECORD
    print()
    for geodata in dwg.objects.query('GEODATA'):
        print(geodata)
        block_record = dwg.get_dxf_entity(geodata.dxf.block_record)
        print('GEODATA object used by {}'.format(block_record.dxf.name))
        pprint(geodata.dxfattribs())
        pprint(geodata.coordinate_system_definition())
        pprint(geodata.get_mesh_data(), width=160)

