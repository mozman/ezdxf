import ezdxf

dwg = ezdxf.readfile("Slider01.dxf")

print(dwg.layout_names())
