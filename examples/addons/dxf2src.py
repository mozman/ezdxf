import ezdxf
from ezdxf.addons.dxf2code import entities_to_code

NAME = "dxf_menger_sponge_v1"
# DXF_FILE = r"D:\Source\dxftest\CADKitSamples\{}.dxf".format(NAME)
DXF_FILE = r"C:\Users\manfred\Desktop\Outbox\{}.dxf".format(NAME)
SOUCE_CODE_FILE = r"C:\Users\manfred\Desktop\Outbox\{}.py".format(NAME)

doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

source = entities_to_code(msp)

print('writing ' + SOUCE_CODE_FILE)
with open(SOUCE_CODE_FILE, mode='wt') as f:
    source.writelines(f)

print('done.')
