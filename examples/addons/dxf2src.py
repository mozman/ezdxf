import ezdxf
from ezdxf.addons.dxf2code import entities_to_code

DXF_FILE = r"D:\Source\dxftest\CADKitSamples\A_000217.dxf"
SOUCE_CODE_FILE = r"C:\Users\manfred\Desktop\Outbox\A_000217.py"

doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

source = entities_to_code(msp)

print('writing ' + SOUCE_CODE_FILE)
with open(SOUCE_CODE_FILE, mode='wt') as f:
    source.writelines(f)

print('done.')
