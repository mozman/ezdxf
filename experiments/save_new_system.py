import ezdxf
from ezdxf.lldxf.const import versions_supported_by_save, acad_release
OUTPATH = r"C:\Users\manfred\Desktop\Outbox\{}.dxf"
doc = ezdxf.new2(setup=True)

for version in versions_supported_by_save:
    doc.dxfversion = version
    doc.saveas(filename=OUTPATH.format(acad_release[version]))
