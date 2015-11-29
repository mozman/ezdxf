import ezdxf

LEGACY_DXF = "Design51_AC1003.dxf"
R12_DXF = "Design51_AC1009.dxf"

dwg = ezdxf.readfile(LEGACY_DXF)  # DXF file version AC1003
dwg.saveas(R12_DXF)
