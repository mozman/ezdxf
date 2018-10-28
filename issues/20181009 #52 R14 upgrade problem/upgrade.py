import ezdxf

IN_FILE = "ProE-R14.dxf"
OUT_FILE = "ProE-R2000.dxf"

dwg = ezdxf.readfile(IN_FILE)
dwg.saveas(OUT_FILE)
